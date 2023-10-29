import os
from pathlib import Path

from ..exceptions import TemplateFileNotFoundError
from .base import AbstractPrompt


class FileBasedPrompt(AbstractPrompt):
    """Base class for prompts supposed to read template content from a file.

    `_path_to_template` attribute has to be specified.
    """

    _path_to_template: str

    def __init__(self, **kwargs):
        if (template_path := kwargs.pop("path_to_template", None)) is not None:
            self._path_to_template = template_path
        else:
            current_dir_path = Path(__file__).parent
            self._path_to_template = os.path.join(
                current_dir_path, "..", self._path_to_template
            )

        super().__init__(**kwargs)

    @property
    def template(self) -> str:
        try:
            with open(self._path_to_template) as fp:
                return fp.read()
        except FileNotFoundError as e:
            raise TemplateFileNotFoundError(
                self._path_to_template, self.__class__.__name__
            ) from e
        except IOError as exc:
            raise RuntimeError(
                f"Failed to read template file '{self._path_to_template}': {exc}"
            ) from exc
