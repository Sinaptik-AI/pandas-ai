""" Base class to implement a new Prompt
In order to better handle the instructions, this prompt module is written.
"""

import os
import re
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader


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
            path_to_template = os.path.join(current_dir_path, "templates")
            env = Environment(loader=FileSystemLoader(path_to_template))
            self.prompt = env.get_template(self.template_path)

        self._resolved_prompt = None

    def render(self):
        """Render the prompt."""
        render = self.prompt.render(**self.props)

        # Remove additional newlines in render
        render = re.sub(r"\n{3,}", "\n\n", render)

        return render

    def to_string(self):
        """Render the prompt."""
        if self._resolved_prompt is None:
            self._resolved_prompt = self.prompt.render(**self.props)

        return self._resolved_prompt

    def __str__(self):
        return self.to_string()

    def validate(self, output: str) -> bool:
        return isinstance(output, str)

    def to_json(self):
        """
        Return Json Prompt
        """
        if "context" not in self.props:
            return {"prompt": self.to_string()}

        context = self.props["context"]
        memory = context.memory
        conversations = memory.to_json()
        system_prompt = memory.get_system_prompt()
        return {
            "conversation": conversations,
            "system_prompt": system_prompt,
            "prompt": self.to_string(),
        }
