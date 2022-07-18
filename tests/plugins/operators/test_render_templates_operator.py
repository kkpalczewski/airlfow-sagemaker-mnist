import pytest
import importlib_resources

from mnist_classifier.plugins.operators.render_templates_operator import RenderTemplatesOperator


@pytest.mark.parametrize("template_path",
                         [f.name for f in importlib_resources.files("mnist_classifier.templates").iterdir() if
                          f.name not in ["__init__.py", "__pycache__"]])
def test_render_templates_operator(template_path,
                                   templates_all_templates_templated_fields):
    pytest.helpers.operator_test(
        operator=RenderTemplatesOperator,
        operator_params={
            "template_name": template_path,
            "template_params": templates_all_templates_templated_fields[template_path]
        }
    )
