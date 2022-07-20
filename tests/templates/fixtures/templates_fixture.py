import glob
import os
import json
from typing import Dict
from pathlib import Path
from datetime import datetime
from airflow.models import Variable

import pytest


@pytest.fixture
def templates_in_module():
    return "mnist_classifier.templates"


@pytest.fixture
def templates_all_templates_templated_fields() -> Dict:
    return {
        "sagemaker_train_config.json.jinja": {
            "execution_date": datetime.today(),
            "mnist_bucket": Variable.get('mnist_bucket'),
            "model_arn_role": Variable.get("model_arn_role"),
            "save_extracted_path": "extarcted_path",
            "mnist_training_image": Variable.get('mnist_training_image')
        },
        "sagemaker_deploy_config.json.jinja": {
            "execution_date": datetime.today(),
            "mnist_bucket": Variable.get('mnist_bucket'),
            "model_arn_role": Variable.get("model_arn_role"),
            "mnist_training_image": Variable.get('mnist_training_image')
        }
    }

@pytest.fixture
def templates_all_templates_raw(templates_in_module,
                                templates_all_templates_templated_fields) -> Dict:
    from importlib.resources import files

    template_paths = [f for f in files(templates_in_module).iterdir() if f != "__init__.py"]

    unhandled_templates = set([template_path.name for template_path in template_paths]).\
        difference(*templates_all_templates_templated_fields)
    assert len(unhandled_templates) == 0, f"Templates {unhandled_templates} not included in tests!"

    templates_raw = dict()

    for template_path in template_paths:
        template_path = str(template_path)
        with open(template_path) as f:
            template = json.load(f)
        templates_raw[template_path] = template

    return templates_raw
