import re
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from typing import Optional
from pathlib import Path

from pandasai.exceptions import PromptTemplateNotFound


class BasePrompt:
    """Base class to implement a new Prompt.

    Inheritors have to override `template` property.
    """

    template: Optional[str] = None
    template_path: Optional[str] = None

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
            try:
                env = Environment(loader=FileSystemLoader(path_to_template))
                self.prompt = env.get_template(self.template_path)
            except TemplateNotFound as e:
                raise PromptTemplateNotFound(
                    f"Template not found: {self.template_path}"
                ) from e

    def render(self):
        """Render the prompt."""
        render = self.prompt.render(**self.props)

        # Remove additional newlines in render
        render = re.sub(r"\n{3,}", "\n\n", render)

        return render

    def to_string(self):
        """Render the prompt."""
        return self.prompt.render(**self.props)

    def __str__(self):
        return self.to_string()

    def validate(self, output: str) -> bool:
        return isinstance(output, str)
