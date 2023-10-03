""" Base class to implement a new Prompt
In order to better handle the instructions, this prompt module is written.
"""
from abc import ABC, abstractmethod

from pandasai.helpers.path import find_closest

from ..exceptions import TemplateFileNotFoundError


class AbstractPrompt(ABC):
    """Base class to implement a new Prompt.

    Inheritors have to override `template` property.
    """

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
    def template(self) -> str:
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
    """Base class for prompts supposed to read template content from a file.

    `_path_to_template` attribute has to be specified.
    """

    _path_to_template: str

    def __init__(self, **kwargs):
        if (template_path := kwargs.pop("path_to_template", None)) is not None:
            self._path_to_template = template_path
        else:
            self._path_to_template = find_closest(self._path_to_template)

        super().__init__(**kwargs)

    @property
    def template(self) -> str:
        try:
            with open(self._path_to_template) as fp:
                return fp.read()
        except FileNotFoundError:
            raise TemplateFileNotFoundError(
                self._path_to_template, self.__class__.__name__
            )
        except IOError as exc:
            raise RuntimeError(
                f"Failed to read template file '{self._path_to_template}': {exc}"
            )
