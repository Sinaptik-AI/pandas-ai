""" Base class to implement a new Prompt
In order to better handle the instructions, this prompt module is written.
"""
import os
from abc import ABC, abstractmethod


class AbstractPrompt(ABC):
    """Base class to implement a new Prompt"""

    _args = {}

    def __init__(self, **kwargs):
        """
        __init__ method of Base class of Prompt Module
        Args:
            **kwargs: Inferred Keyword Arguments
        """
        if kwargs:
            self._args = kwargs

    def _generate_dataframes(self, dfs):
        """
        Generate the dataframes metadata
        Args:
            dfs: List of Dataframes
        """
        dataframes = []
        for index, df in enumerate(dfs, start=1):
            description = """<dataframe>
Dataframe """
            if df.table_name is not None:
                description += f"{df.table_name} (dfs[{index-1}])"
            else:
                description += f"dfs[{index-1}]"
            description += (
                f", with {df.rows_count} rows and {df.columns_count} columns."
            )
            if df.table_description is not None:
                description += f"\nDescription: {df.table_description}"
            description += f"""
This is the metadata of the dataframe dfs[{index-1}]:
{df.head_csv}</dataframe>"""  # noqa: E501
            dataframes.append(description)

        return "\n\n".join(dataframes)

    @property
    @abstractmethod
    def template(self):
        ...

    def set_var(self, var, value):
        if var == "dfs":
            self._args["dataframes"] = self._generate_dataframes(value)
        self._args[var] = value

    def to_string(self):
        return self.template.format(**self._args)

    def __str__(self):
        return self.to_string()


class FileBasedPrompt(AbstractPrompt):
    _path_to_template: str

    def __init__(self, **kwargs):
        if (template_path := kwargs.pop("path_to_template", None)) is not None:
            self._path_to_template = template_path

        super().__init__(**kwargs)

    @property
    def template(self):
        if not os.path.exists(self._path_to_template):
            raise FileNotFoundError(
                f"Unable to find a file with template at '{self._path_to_template}' "
                f"for '{self.__class__.__name__}' prompt."
            )
        with open(self._path_to_template) as fp:
            return fp.read()
