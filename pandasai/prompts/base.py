""" Base class to implement a new Prompt
In order to better handle the instructions, this prompt module is written.
"""
from abc import ABC, abstractmethod
import string

from pandasai.helpers.dataframe_serializer import DataframeSerializer


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
        for index, df in enumerate(dfs):
            print("OOPPPPPPPPKMMMM", self._config)
            dataframe_info = DataframeSerializer().serialize(
                df, extras={"index": index}, type_=self._config.dataframe_serializer
            )
            print(dataframe_info)
            dataframes.append(dataframe_info)

        return "\n".join(dataframes)

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

        if "dfs" in vars:
            self._args["dataframes"] = self._generate_dataframes(vars["dfs"])

        self._args.update(vars)

    def to_string(self):
        self.on_prompt_generation()

        prompt_args = {}
        for key, value in self._args.items():
            if isinstance(value, AbstractPrompt):
                args = [
                    arg[1] for arg in string.Formatter().parse(value.template) if arg[1]
                ]
                value.set_vars(
                    {k: v for k, v in self._args.items() if k != key and k in args}
                )
                prompt_args[key] = value.to_string()
            else:
                prompt_args[key] = value

        return self.template.format_map(prompt_args)

    def __str__(self):
        return self.to_string()

    def validate(self, output: str) -> bool:
        return isinstance(output, str)
