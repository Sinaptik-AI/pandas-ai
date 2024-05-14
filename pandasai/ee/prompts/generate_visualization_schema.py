import json
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

from ...prompts.base import BasePrompt


class GenerateVisualizationSchemaPrompt(BasePrompt):
    """Prompt to generate Python code with SQL from a dataframe."""

    template_path = "generate_visualization_schema.tmpl"

    def __init__(self, **kwargs):
        """Initialize the prompt."""
        self.props = kwargs

        if self.template:
            env = Environment()
            self.prompt = env.from_string(self.template)
        elif self.template_path:
            # find path to template file
            current_dir_path = Path(__file__).parent

            path_to_template = current_dir_path / "templates"
            env = Environment(loader=FileSystemLoader(path_to_template))
            self.prompt = env.get_template(self.template_path)

        self._resolved_prompt = None

    def validate(self, output) -> bool:
        try:
            output = output.replace("# SAMPLE SCHEMA", "")
            json_data = json.loads(output)
            return isinstance(json_data, List)
        except json.JSONDecodeError:
            return False
