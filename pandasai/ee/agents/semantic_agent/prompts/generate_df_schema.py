import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pandasai.ee.helpers.json_helper import extract_json_from_json_str
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
            json_data = extract_json_from_json_str(
                output.replace("# SAMPLE SCHEMA", "")
            )
            context = self.props["context"]
            if isinstance(json_data, dict):
                json_data = [json_data]
            if isinstance(json_data, list):
                for record in json_data:
                    if not all(key in record for key in ("name", "table")):
                        return False

                return len(context.dfs) == len(json_data)

        except json.JSONDecodeError:
            pass
        return False

    def to_json(self):
        context = self.props["context"]
        memory = context.memory
        conversations = memory.to_json()
        system_prompt = memory.get_system_prompt()
        return {
            "conversation": conversations,
            "system_prompt": system_prompt,
            "prompt": self.to_string(),
        }
