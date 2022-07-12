import pytest


@pytest.fixture(scope="session")
def dummy_project_tree(tmp_path_factory):
    """
    Tree:
    - tests
        - dags
        - src
            - fixtures
                - mock_api_fixture.py
                - searches_fixture.py
                _ __init__.py
        - helpers
            - text.txt

    :param tmp_path:
    :return:
    """
    tests_tmp_path = tmp_path_factory.mktemp("tests")
    (tests_tmp_path / "dags").mkdir(parents=True, exist_ok=True)
    (tests_tmp_path / "src/fixtures/mock_api_fixture.py").mkdir(
        parents=True, exist_ok=True
    )
    (tests_tmp_path / "src/fixtures/searches_fixture.py").mkdir(
        parents=True, exist_ok=True
    )
    (tests_tmp_path / "src/fixtures/__init__.py").mkdir(parents=True, exist_ok=True)
    (tests_tmp_path / "helpers/text.txt").mkdir(parents=True, exist_ok=True)

    return tests_tmp_path


@pytest.fixture(scope="session")
def tests_dirname(dummy_project_tree) -> str:

    return str(dummy_project_tree).split("/")[-1]
