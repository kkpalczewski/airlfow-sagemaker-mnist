import json
import pytest
from pathlib import Path
from mnist_classifier.model.utils import render_config
import importlib_resources


@pytest.mark.parametrize("template_path", [str(f) for f in importlib_resources.files("mnist_classifier.templates").iterdir() if
                          f.name not in ["__init__.py", "__pycache__"]])
def test_render_config(templates_all_templates_templated_fields,
                       template_path):
    with open(template_path) as f:
        template = json.load(f)

    templates_params = templates_all_templates_templated_fields[Path(template_path).name]

    render_config(template, templates_params)
