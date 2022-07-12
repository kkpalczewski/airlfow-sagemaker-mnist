from airflow import DAG
import requests
from airflow.decorators import task, dag
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime


@task
def download_mnist_to_s3(
    bucket_name,
    save_path,
    skip_if_exists: bool = False,
    download_address: str = "https://github.com/mnielsen/neural-networks-and-deep-learning/raw/master/data/mnist.pkl.gz"
):
    """Download mnist and save it in S3"""

    response = requests.get(download_address)

    s3_hook = S3Hook()
    if not s3_hook.check_for_bucket(bucket_name):
        s3_hook.create_bucket(bucket_name)

    if skip_if_exists and

@dag(schedule_interval="@daily", start_date=datetime(2021, 12, 1), catchup=False)
def mnist_classifier():
    download_mnist_to_s3()


def _extract_mnist():
    pass
