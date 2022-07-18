from typing import Union, Type
import os
from glob import glob
import os
import pytest
from pathlib import Path
from moto import mock_s3, mock_sagemaker
import pendulum
from airflow.models import DagBag
from airflow.models.dag import DAG, DagRun
from airflow.operators.python import PythonOperator
from airflow.utils.state import State
from airflow.decorators.base import _TaskDecorator, BaseOperator

pytest_plugins = ["helpers_namespace"]


@pytest.fixture(autouse=True, scope="session")
def set_env_vars_and_init_tmp_dir(tmp_path_factory):
    old_environ = os.environ.copy()

    os.environ["AIRFLOW__CORE__DAGS_FOLDER"] = str(
        Path(os.path.dirname(os.path.abspath(__file__))) / "../dags"
    )
    os.environ["AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS"] = "False"
    os.environ["AIRFLOW_CORE_LOAD_EXAMPLES"] = "False"
    os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "True"
    os.environ["AIRFLOW_HOME"] = os.path.dirname(os.path.dirname(__file__))
    tmp_dir = tmp_path_factory.getbasetemp()
    os.environ["AIRFLOW_VAR_BASE_DIR"] = str(tmp_dir)
    os.environ["AIRFLOW__CORE__EXECUTOR"] = "DebugExecutor"
    os.environ["AIRFLOW__CORE__ENABLE_XCOM_PICKLING"] = "true"
    os.environ["AIRFLOW_VAR_MNIST_BUCKET"] = "mnist-bucket"
    os.environ["AIRFLOW_VAR_MNIST_TRAINING_IMAGE"] = "438346466558.dkr.ecr.eu-west-1.amazonaws.com/kmeans:1"
    os.environ["AIRFLOW_VAR_MODEL_ARN_ROLE"] = "arn:aws:iam::111222333444:role/service-role/AmazonSageMaker-ExecutionRole"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

    yield

    os.environ.clear()
    os.environ.update(old_environ)


@pytest.fixture(autouse=True, scope="session")
def reset_db():
    """Reset the Airflow metastore for every test session"""
    from airflow.utils import db

    db.resetdb()
    yield


@pytest.fixture(autouse=True)
def moto_boto_mock():
    mocks3 = mock_s3()
    mocksagemaker = mock_sagemaker()

    mocks3.start()
    mocksagemaker.start()
    yield
    mocks3.stop()
    mocksagemaker.stop()


@pytest.fixture(scope="session")
def dag_bag():
    return DagBag(
        dag_folder=os.environ["AIRFLOW__CORE__DAGS_FOLDER"], include_examples=False
    )


@pytest.helpers.register
def operator_test(
        operator: Union[_TaskDecorator, Type[BaseOperator]],
        operator_params,
        start_date=pendulum.today("UTC").add(days=-1),
        end_date=pendulum.today("UTC").add(days=-1),
):
    """Testing taskflow task"""
    with DAG(
            dag_id="test_dag",
            start_date=start_date,
            end_date=end_date,
            schedule_interval="@daily",
    ) as dag:
        if isinstance(operator, _TaskDecorator):
            task = PythonOperator(
                task_id="test_task",
                python_callable=operator.function,
                **operator_params
            )
        else:
            task = operator(
                task_id="test_task",
                **operator_params
            )

        dag.clear()
        task.run(start_date=dag.start_date, end_date=dag.end_date)
    dagruns = DagRun.find(dag_id=dag.dag_id, execution_date=dag.start_date)

    assert len(dagruns) == 1
    assert dagruns[0].get_task_instance("test_task").state == State.SUCCESS

@pytest.helpers.register
def get_plugins(plugin_dir: Union[str, Path], root_dir: str = "tests"):
    """Get plugins from specific dirs. Used in pytest_plugins."""
    if isinstance(plugin_dir, str):
        plugin_dir = Path(plugin_dir)

    dir_from_tests_root = find_directory_from_root_dir(root_dir, plugin_dir)
    plugin_files = [
        fixture.split("/")[-1]
        for fixture in glob(str(plugin_dir / "*"))
        if "__" not in fixture and fixture.endswith(".py")
    ]
    plugins = [
        parse_string_to_module("/".join([dir_from_tests_root, fixture]))
        for fixture in plugin_files
    ]
    return plugins


def find_directory_from_root_dir(
        root_dirname: str = "tests", final_dir: Path = "."
) -> str:
    """Find path from specific root dir. Last root dir is searched."""
    current_path_abs = final_dir.resolve()
    last_index = [
        i for i, dir in enumerate(current_path_abs.parts) if dir == root_dirname
    ][-1]

    return str(Path(*current_path_abs.parts[last_index:]))


def parse_string_to_module(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")


pytest_plugins = pytest.helpers.get_plugins(
    os.path.dirname(__file__) + "/templates/fixtures"
)
