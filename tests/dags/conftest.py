import os
from pathlib import Path
import pendulum
import pytest


@pytest.fixture
def start_date():
    return pendulum.today("UTC").add(days=-1)


@pytest.fixture
def end_date():
    return pendulum.today("UTC").add(days=-1)


@pytest.fixture
def mnist_download_address():
    return "https://github.com/mnielsen/neural-networks-and-deep-learning/raw/master/data/mnist.pkl.gz"  # pylint:disable=line-too-long # noqa: E501


@pytest.fixture
def mnist_contents_test_path():
    return Path(os.path.dirname(os.path.abspath(__file__))) / "contents/mnist.pkl.gz"


@pytest.fixture
def mnist_contents_test(mnist_contents_test_path) -> bin:
    with open(mnist_contents_test_path, "rb") as f:
        mnist_contents_test = f.read()
    return mnist_contents_test


@pytest.fixture
def mnist_raw_path(start_date):
    return f"raw/{start_date.strftime('%Y%m%d')}.pkl.gz"


@pytest.fixture
def mnist_train_data_path():
    return Path(os.path.dirname(os.path.abspath(__file__))) / "contents/mnist_train"


@pytest.fixture
def mnist_train_data(mnist_train_data_path) -> bin:
    with open(mnist_train_data_path, "rb") as f:
        mnist_train_data = f.read()
    return mnist_train_data


@pytest.fixture
def mnist_extracted_path(start_date):
    return f"extracted/{start_date.strftime('%Y%m%d')}"


@pytest.fixture
def bucket_name():
    return "mnist_classifier"


@pytest.fixture(autouse=True)
def mnist_download_mock(requests_mock, mnist_download_address, mnist_contents_test):
    requests_mock.real_http = True

    requests_mock.get(mnist_download_address, content=mnist_contents_test)
