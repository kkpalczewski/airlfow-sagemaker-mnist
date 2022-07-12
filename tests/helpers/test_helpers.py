import os
import pytest


@pytest.fixture
def cd_src(dummy_project_tree):
    initial_path = os.getcwd()
    os.chdir(dummy_project_tree / "src")
    yield
    os.chdir(initial_path)


def test_get_plugins_from_fixtures_starting_from_src(
    dummy_project_tree, tests_dirname, cd_src
):
    test_plugins = pytest.helpers.get_plugins(
        root_dir=tests_dirname, plugin_dir="fixtures"
    )
    actual_plugins = [
        ".".join([tests_dirname, "src", "fixtures", "mock_api_fixture"]),
        ".".join([tests_dirname, "src", "fixtures", "searches_fixture"]),
    ]
    assert sorted(actual_plugins) == sorted(test_plugins)


@pytest.fixture
def cd_tests(dummy_project_tree):
    initial_path = os.getcwd()
    os.chdir(dummy_project_tree)
    yield
    os.chdir(initial_path)


def test_get_plugins_from_dags_starting_from_tests(
    dummy_project_tree, tests_dirname, cd_tests
):
    test_plugins = pytest.helpers.get_plugins(root_dir=tests_dirname, plugin_dir="dags")
    actual_plugins = []
    assert sorted(actual_plugins) == sorted(test_plugins)


def test_get_plugins_from_fixtures_starting_from_tests(
    dummy_project_tree, tests_dirname, cd_tests
):
    test_plugins = pytest.helpers.get_plugins(
        root_dir=tests_dirname, plugin_dir="src/fixtures"
    )
    actual_plugins = [
        ".".join([tests_dirname, "src", "fixtures", "mock_api_fixture"]),
        ".".join([tests_dirname, "src", "fixtures", "searches_fixture"]),
    ]
    assert sorted(actual_plugins) == sorted(test_plugins)
