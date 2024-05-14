import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pandasai.prompts.base import BasePrompt


class GenerateDFSchemaPrompt(BasePrompt):
    """Prompt to generate Python code with SQL from a dataframe."""

    template_path = "generate_df_schema.tmpl"

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

    def validate(self, output: str) -> bool:
        try:
            json_data = json.loads(output.replace("# SAMPLE SCHEMA", ""))
            if isinstance(json_data, list):
                for record in json_data:
                    if not all(key in record for key in ("name", "table")):
                        return False
                return True
        except json.JSONDecodeError:
            pass
        return False
