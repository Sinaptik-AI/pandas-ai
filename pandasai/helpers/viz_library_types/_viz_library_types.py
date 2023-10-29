from abc import abstractmethod, ABC
from typing import Any, Iterable


class BaseVizLibraryType(ABC):
    @property
    @abstractmethod
    def template_hint(self) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    def _validate_type(self, actual_type: str) -> bool:
        if actual_type != self.name:
            return False
        return True

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


class MatplotlibVizLibraryType(BaseVizLibraryType):
    @property
    def template_hint(self):
        return """When a user requests to create a chart, utilize the Python matplotlib 
        library to generate high-quality graphics that will be saved 
        directly to a file. 
        If you import matplotlib use the 'agg' backend for rendering plots."""

    @property
    def name(self):
        return "matplotlib"


class PlotlyVizLibraryType(BaseVizLibraryType):
    @property
    def template_hint(self):
        return """When a user requests to create a chart, utilize the Python plotly 
        library to generate high-quality graphics that will be saved 
        directly to a file. 
        If you import matplotlib use the 'agg' backend for rendering plots."""

    @property
    def name(self):
        return "plotly"


class SeabornVizLibraryType(BaseVizLibraryType):
    @property
    def template_hint(self):
        return """When a user requests to create a chart, utilize the Python Seaborn 
        library to generate high-quality graphics that will be saved 
        directly to a file. 
        If you import matplotlib use the 'agg' backend for rendering plots."""

    @property
    def name(self):
        return "seaborn"
