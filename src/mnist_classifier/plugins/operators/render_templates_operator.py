from typing import Dict
import json
from jinja2 import Template
from airflow.decorators.base import BaseOperator
from importlib.resources import path, read_text


class RenderTemplatesOperator(BaseOperator):
    """
    Class which collects
    """
    template_fields = ["_template_params"]
    TEMPLATE_MODULE = "mnist_classifier.templates"

    def __init__(self,
                 template_name,
                 template_params,
                 **kwargs):
        super().__init__(**kwargs)
        self._template_params = template_params
        self._template_name = template_name

    def execute(self, context) -> Dict:
        template = read_text(self.TEMPLATE_MODULE, self._template_name)
        rendered_template = Template(template).render(self._template_params)

        return json.loads(rendered_template)

