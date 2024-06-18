from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pandasai.prompts.base import BasePrompt


class JudgeAgentPrompt(BasePrompt):
    """Prompt to generate Python code from a dataframe."""

    template_path = "judge_agent_prompt.tmpl"

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
