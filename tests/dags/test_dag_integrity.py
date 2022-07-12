import glob
from os import path
import pytest
from airflow import models as airflow_models
from airflow.utils.dag_cycle_tester import check_cycle

DAG_PATHS = glob.glob(path.join(path.dirname(__file__), "..", "..", "dags", "*.py"))


@pytest.mark.parametrize("dag_path", DAG_PATHS)
def test_dag_integrity(dag_path):
    """Import DAG files and check for a valid DAG instance."""
    dag_name = path.basename(dag_path)
    module = _import_file(dag_name, dag_path)
    # Validate if there is at least 1 DAG object in the file
    dag_objects = [
        var for var in vars(module).values() if isinstance(var, airflow_models.DAG)
    ]
    assert dag_objects
    # For every DAG object, test for cycles
    for dag in dag_objects:
        check_cycle(dag)


def _import_file(module_name, module_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_import_errors(dag_bag):
    """
    Tests that the DAG files can be imported by Airflow without errors.
    ie.
        - No exceptions were raised when processing the DAG files,
        be it timeout or other exceptions
        - The DAGs are indeed acyclic
            DagBag.bag_dag() checks for dag.test_cycle()
    """
    assert len(dag_bag.import_errors) == 0
