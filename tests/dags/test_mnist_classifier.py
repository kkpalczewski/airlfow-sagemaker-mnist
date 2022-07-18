import filecmp
import pytest
from airflow.models.dag import DAG, DagRun
from airflow.operators.python import PythonOperator
from airflow.utils.state import State
import boto3

import os

os.environ["AIRFLOW_VAR_MNIST_BUCKET"] = "mnist-bucket"
os.environ["AIRFLOW_VAR_MNIST_TRAINING_IMAGE"] = "438346466558.dkr.ecr.eu-west-1.amazonaws.com/kmeans:1"
os.environ[
    "AIRFLOW_VAR_MODEL_ARN_ROLE"] = "arn:aws:iam::111222333444:role/service-role/AmazonSageMaker-ExecutionRole-20180905T153196"

from dags.mnist_classifier_dag import download_mnist_to_s3, extract_mnist, dag


def test_download_mnist(
        start_date,
        end_date,
        bucket_name,
        mnist_raw_path,
        tmp_path,
        mnist_download_address,
        mnist_contents_test_path,
):
    pytest.helpers.operator_test(
        operator=download_mnist_to_s3,
        operator_params={
            "op_kwargs": {
                "replace": True,
                "download_address": mnist_download_address,
                "bucket_name": bucket_name,
                "save_raw_path": mnist_raw_path,
            }
        },
        start_date=start_date,
        end_date=end_date,
    )

    # download mnist from mocked s3 bucket
    conn = boto3.resource("s3")
    bucket = conn.Bucket(bucket_name)
    download_local_dir = tmp_path / "raw"
    download_local_dir.mkdir(parents=True, exist_ok=True)
    download_local_path = download_local_dir / f"{start_date.strftime('%Y%m%d')}.pkl.gz"
    bucket.download_file(str(mnist_raw_path), str(download_local_path))

    assert filecmp.cmp(download_local_path, mnist_contents_test_path)


@pytest.fixture
def download_mnist_mock(bucket_name, mnist_contents_test, mnist_raw_path):
    # unrecognized mock failure
    aws_default_region = os.environ.get("AWS_DEFAULT_REGION", None)
    if aws_default_region is not None:
        del os.environ["AWS_DEFAULT_REGION"]

    conn = boto3.resource("s3")
    bucket = conn.create_bucket(Bucket=bucket_name)
    bucket.put_object(Body=mnist_contents_test, Key=mnist_raw_path)

    yield
    if aws_default_region is not None:
        os.environ["AWS_DEFAULT_REGION"] = aws_default_region


def test_extract_mnist(
        tmp_path,
        start_date,
        end_date,
        mnist_extracted_path,
        bucket_name,
        mnist_raw_path,
        download_mnist_mock,
        mnist_train_data_path,
):
    pytest.helpers.operator_test(
        operator=extract_mnist,
        operator_params={
            "op_kwargs": {
                "bucket_name": bucket_name,
                "save_raw_path": mnist_raw_path,
                "save_extracted_path": mnist_extracted_path,
            }
        },
        start_date=start_date,
        end_date=end_date,
    )

    # download mnist from mocked s3 bucket
    conn = boto3.resource("s3")
    bucket = conn.Bucket(bucket_name)
    download_local_dir = tmp_path / "extracted"
    download_local_dir.mkdir(parents=True, exist_ok=True)
    download_local_path = download_local_dir / f"{start_date.strftime('%Y%m%d')}"
    bucket.download_file(str(mnist_extracted_path), str(download_local_path))

    assert filecmp.cmp(download_local_path, mnist_train_data_path)


def test_dag(start_date, end_date):
    """Check sample dag execution"""
    dag.clear()
    dag.run(start_date=start_date, end_date=end_date)
    dagruns = DagRun.find(dag_id=dag.dag_id, execution_date=start_date)

    assert len(dagruns) == 1
    assert dagruns[0].state == State.SUCCESS
