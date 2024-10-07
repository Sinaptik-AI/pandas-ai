import pandas as pd
from typing import Optional, Union
from pandasai.schemas.df_config import Config


class DataFrame(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = None

    def chat(self, prompt: str, config: Optional[Union[dict, Config]] = None) -> str:
        """
        Interact with the DataFrame using natural language.

        Args:
            prompt (str): The natural language query or instruction.
            config (Optional[Union[dict, Config]]): Configuration for the chat session.

        Returns:
            str: The response to the prompt.
        """
        from pandasai.agent import Agent

        if config:
            self._config = Config(**config) if isinstance(config, dict) else config
        elif self._config is None:
            self._config = Config()

        agent = Agent([self], config=self._config)
        return agent.chat(prompt)

    @classmethod
    def from_pandas(cls, df: pd.DataFrame) -> "DataFrame":
        """
        Create a PandasAI DataFrame from a pandas DataFrame.

        Args:
            df (pd.DataFrame): The pandas DataFrame to convert.

        Returns:
            DataFrame: A new PandasAI DataFrame instance.
        """
        return cls(df)
