""" Base class to implement a new Prompt
In order to better handle the instructions, this prompt module is written.
"""
from abc import ABC, abstractmethod


class AbstractPrompt(ABC):
    """Base class to implement a new Prompt.

    Inheritors have to override `template` property.
    """

    _args: dict = None
    _config: dict = None

    def __init__(self, **kwargs):
        """
        __init__ method of Base class of Prompt Module
        Args:
            **kwargs: Inferred Keyword Arguments
        """
        if self._args is None:
            self._args = {}

        self._args.update(kwargs)
        self.setup(**kwargs)

    def setup(self, **kwargs) -> None:
        pass

    def on_prompt_generation(self) -> None:
        pass

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

    def set_config(self, config):
        self._config = config

    def get_config(self, key=None):
        if self._config is None:
            return None
        if key is None:
            return self._config
        if hasattr(self._config, key):
            return getattr(self._config, key)

    def set_var(self, var, value):
        if self._args is None:
            self._args = {}

        if var == "dfs":
            self._args["dataframes"] = self._generate_dataframes(value)
        self._args[var] = value

    def set_vars(self, vars):
        if self._args is None:
            self._args = {}
        self._args.update(vars)

    def to_string(self):
        self.on_prompt_generation()

        prompt_args = {}
        for key, value in self._args.items():
            if isinstance(value, AbstractPrompt):
                value.set_vars(
                    {
                        k: v
                        for k, v in self._args.items()
                        if k != key and not isinstance(v, AbstractPrompt)
                    }
                )
                prompt_args[key] = value.to_string()
            else:
                prompt_args[key] = value

        return self.template.format_map(prompt_args)

    def __str__(self):
        return self.to_string()

    def validate(self, output: str) -> bool:
        return isinstance(output, str)
