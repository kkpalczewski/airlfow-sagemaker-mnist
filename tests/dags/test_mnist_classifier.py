import filecmp
import os
from pathlib import Path
import requests
import pytest
import pendulum
from airflow.models.dag import DAG, DagRun
from airflow.operators.python import PythonOperator
from airflow.utils.state import State
from dags.mnist_classifier import download_mnist_to_s3, mnist_classifier
from helpers.common import add_base_dir_if_exists
from moto import mock_s3
import boto3


def test_download():
    response = requests.get(
        "https://github.com/mnielsen/neural-networks-and-deep-learning/raw/master/data/mnist.pkl.gz"
    )
    print(response)


@mock_s3
def test_download_mnist(
    start_date,
    end_date,
    bucket_name,
    mnist_raw_path,
    tmp_path,
    mnist_download_address,
    mnist_contents_test_path,
):
    with DAG(
        dag_id="test_dag",
        start_date=start_date,
        end_date=end_date,
        schedule_interval="@daily",
    ) as dag:
        task = PythonOperator(
            task_id="download_mnist",
            python_callable=download_mnist_to_s3.function,
            op_kwargs={
                "skip_if_exists": True,
                "download_address": mnist_download_address,
                "bucket_name": bucket_name,
                "save_path": mnist_raw_path,
            },
        )

        dag.clear()
        task.run(start_date=dag.start_date, end_date=dag.end_date)
    dagruns = DagRun.find(dag_id=dag.dag_id, execution_date=dag.start_date)

    assert len(dagruns) == 1
    assert dagruns[0].get_task_instance("download_mnist").state == State.SUCCESS

    # download mnist from mocked s3 bucket
    conn = boto3.resource("s3")
    bucket = conn.Bucket(bucket_name)
    download_local_dir = tmp_path / "raw"
    download_local_dir.mkdir(parents=True, exist_ok=True)
    download_local_path = download_local_dir / f"{start_date.strftime('%Y%m%d')}.pkl.gz"
    bucket.download_file(str(mnist_raw_path), str(download_local_path))

    assert filecmp.cmp(download_local_path, mnist_contents_test_path)


def test_extract_mnist():
    assert False


def test_sagemaker_train():
    assert False


def test_sagemaker_deploy():
    assert False
