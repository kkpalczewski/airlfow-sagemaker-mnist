import io
import gzip
import pickle
import datetime
import pendulum
import requests
from airflow.decorators import task, dag
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
from sagemaker.amazon.common import write_numpy_to_dense_tensor
from mnist_classifier.plugins.operators.render_templates_operator import RenderTemplatesOperator
from airflow.providers.amazon.aws.operators.sagemaker import (
    SageMakerTrainingOperator, SageMakerEndpointOperator
)


@task(multiple_outputs=True)
def download_mnist_to_s3(
        bucket_name,
        save_raw_path,
        replace: bool = True,
        download_address: str = "https://github.com/mnielsen/neural-networks-and-deep-learning/raw/master/data/mnist.pkl.gz"
        # noqa: E501
):
    """Download mnist and save it in S3"""

    response = requests.get(download_address)
    response.raise_for_status()

    s3_hook = S3Hook()
    if not s3_hook.check_for_bucket(bucket_name):
        s3_hook.create_bucket(bucket_name)
    s3_hook.load_bytes(response.content, save_raw_path, bucket_name, replace=replace)

    return {"bucket_name": bucket_name, "save_raw_path": save_raw_path}


@task
def extract_mnist(
        bucket_name, save_raw_path, save_extracted_path, replace: bool = True
):
    s3hook = S3Hook()
    # Download S3 dataset into memory
    mnist_buffer = io.BytesIO()
    mnist_obj = s3hook.get_key(bucket_name=bucket_name, key=save_raw_path)
    mnist_obj.download_fileobj(mnist_buffer)

    # Unpack gzip file, extract dataset, convert to dense tensor, upload back to S3
    mnist_buffer.seek(0)

    with gzip.GzipFile(fileobj=mnist_buffer, mode="rb") as f:
        train_set, _, _ = pickle.loads(f.read(), encoding="latin1")
        output_buffer = io.BytesIO()
        write_numpy_to_dense_tensor(
            file=output_buffer, array=train_set[0], labels=train_set[1]
        )
        output_buffer.seek(0)

        s3hook.load_file_obj(
            output_buffer,
            key=save_extracted_path,
            bucket_name=bucket_name,
            replace=replace,
        )

    return save_extracted_path


@dag(
    schedule_interval="@daily",
    start_date=pendulum.today("UTC").add(days=-1),
    catchup=False,
    render_template_as_native_obj=True,
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": datetime.timedelta(seconds=3),
    },
)
def mnist_classifier_dag():
    download_mnist_to_s3_response = download_mnist_to_s3(
        bucket_name=Variable.get("mnist_bucket"),
        save_raw_path="raw/{{ds_nodash}}.pkl.gz",
    )

    extract_mnist_task = extract_mnist(
        Variable.get("mnist_bucket"),
        download_mnist_to_s3_response["save_raw_path"],
        save_extracted_path="extracted/{{ds_nodash}}",
    )

    render_train_config = RenderTemplatesOperator(
        task_id="render_train_config",
        template_name="sagemaker_train_config.json.jinja",
        template_params={
            "execution_date": "{{execution_date.strftime('%Y-%m-%d-%H-%M-%S')}}",
            "mnist_bucket": Variable.get("mnist_bucket"),
            "model_arn_role": Variable.get("model_arn_role"),
            "save_extracted_path": "{{ti.xcom_pull(task_ids='extract_mnist')}}",
            "mnist_training_image": Variable.get("mnist_training_image")
        }
    )

    sagemaker_train_model = SageMakerTrainingOperator(
        task_id="sagemaker_train_model",
        config="{{ti.xcom_pull(task_ids='render_train_config')}}",
        print_log=False,
        check_interval=10
    )

    render_deploy_config = RenderTemplatesOperator(
        task_id="render_deploy_config",
        template_name="sagemaker_deploy_config.json.jinja",
        template_params={
            "execution_date": "{{execution_date.strftime('%Y-%m-%d-%H-%M-%S')}}",
            "mnist_bucket": Variable.get("mnist_bucket"),
            "model_arn_role": Variable.get("model_arn_role"),
            "mnist_training_image": Variable.get("mnist_training_image")
        }
    )

    sagemaker_deploy_model = SageMakerEndpointOperator(
        task_id="sagemaker_deploy_model",
        operation="update",
        wait_for_completion=True,
        config="{{ti.xcom_pull(task_ids='render_deploy_config')}}"
    )

    extract_mnist_task >> render_train_config >> sagemaker_train_model >> render_deploy_config >> sagemaker_deploy_model


dag = mnist_classifier_dag()
