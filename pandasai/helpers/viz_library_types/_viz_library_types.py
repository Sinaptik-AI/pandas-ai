from abc import abstractmethod, ABC
from typing import Any, Iterable
from pandasai.prompts.generate_python_code import VizLibraryPrompt


class BaseVizLibraryType(ABC):
    @property
    def template_hint(self) -> str:
        return VizLibraryPrompt(library=self.name)

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    def _validate_type(self, actual_type: str) -> bool:
        return actual_type == self.name

    def validate(self, result: dict[str, Any]) -> tuple[bool, Iterable[str]]:
        """
        Validate 'type' and 'constraint' from the result dict.

        Args:
            result (dict[str, Any]): The result of code execution in
                dict representation. Should have the following schema:
                {
                    "viz_library_type": <viz_library_name>
                }

        Returns:
             (tuple(bool, Iterable(str)):
                Boolean value whether the result matches output type
                and collection of logs containing messages about
                'type' mismatches.
        """
        validation_logs = []
        actual_type = result.get("type")

        type_ok = self._validate_type(actual_type)
        if not type_ok:
            validation_logs.append(
                f"The result dict contains inappropriate 'type'. "
                f"Expected '{self.name}', actual '{actual_type}'."
            )

        return type_ok, validation_logs


class NoVizLibraryType(BaseVizLibraryType):
    @property
    def template_hint(self) -> str:
        return ""

    @property
    def name(self):
        return "no_viz_library"


class MatplotlibVizLibraryType(BaseVizLibraryType):
    @property
    def name(self):
        return "matplotlib"


class PlotlyVizLibraryType(BaseVizLibraryType):
    @property
    def name(self):
        return "plotly"


class SeabornVizLibraryType(BaseVizLibraryType):
    @property
    def name(self):
        return "seaborn"
