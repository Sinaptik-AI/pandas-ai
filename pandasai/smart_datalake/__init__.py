"""
A smart dataframe class is a wrapper around the pandas/polars dataframe that allows you
to query it using natural language. It uses the LLMs to generate Python code from
natural language and then executes it on the dataframe.

Example:
    ```python
    from pandasai.smart_dataframe import SmartDataframe
    from pandasai.llm.openai import OpenAI

    df = pd.read_csv("examples/data/Loan payments data.csv")
    llm = OpenAI()

    df = SmartDataframe(df, config={"llm": llm})
    response = df.chat("What is the average loan amount?")
    print(response)
    # The average loan amount is $15,000.
    ```
"""
import uuid
from typing import Any, List, Optional, Union

from pandasai.agent.base import Agent
from pandasai.skills import Skill

from ..helpers.cache import Cache
from ..helpers.df_info import DataFrameType
from ..schemas.df_config import Config


class SmartDatalake:
    def __init__(
        self,
        dfs: List[Union[DataFrameType, Any]],
        config: Optional[Union[Config, dict]] = None,
    ):
        """
        Args:
            dfs (List[Union[DataFrameType, Any]]): List of dataframes to be used
            config (Union[Config, dict], optional): Config to be used. Defaults to None.
        """
        self._agent = Agent(dfs, config=config)

    def add_skills(self, *skills: Skill):
        """
        Add Skills to PandasAI
        """
        self._agent.add_skills(*skills)

    def chat(self, query: str, output_type: Optional[str] = None):
        """
        Run a query on the dataframe.

        Args:
            query (str): Query to run on the dataframe
            output_type (Optional[str]): Add a hint for LLM which
                type should be returned by `analyze_data()` in generated
                code. Possible values: "number", "dataframe", "plot", "string":
                    * number - specifies that user expects to get a number
                        as a response object
                    * dataframe - specifies that user expects to get
                        pandas/polars dataframe as a response object
                    * plot - specifies that user expects LLM to build
                        a plot
                    * string - specifies that user expects to get text
                        as a response object
                If none `output_type` is specified, the type can be any
                of the above or "text".

        Raises:
            ValueError: If the query is empty
        """
        return self._agent.chat(query, output_type)

    def clear_memory(self):
        """
        Clears the memory
        """
        self._agent.clear_memory()

    @property
    def last_prompt(self):
        return self._agent.last_prompt

    @property
    def last_prompt_id(self) -> uuid.UUID:
        """Return the id of the last prompt that was run."""
        if self._agent.last_prompt_id is None:
            raise ValueError("Pandas AI has not been run yet.")
        return self._agent.last_prompt_id

    @property
    def logs(self):
        return self._agent.logger.logs

    @property
    def logger(self):
        return self._agent.logger

    @logger.setter
    def logger(self, logger):
        self._agent.logger = logger

    @property
    def config(self):
        return self._agent.context.config

    @property
    def cache(self):
        return self._agent.context.cache

    @property
    def verbose(self):
        return self._agent.context.config.verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        self._agent.context.config.verbose = verbose
        self._agent.logger.verbose = verbose

    @property
    def save_logs(self):
        return self._agent.context.config.save_logs

    @save_logs.setter
    def save_logs(self, save_logs: bool):
        self._agent.context.config.save_logs = save_logs
        self._agent.logger.save_logs = save_logs

    @property
    def enforce_privacy(self):
        return self._agent.context.config.enforce_privacy

    @enforce_privacy.setter
    def enforce_privacy(self, enforce_privacy: bool):
        self._agent.context.config.enforce_privacy = enforce_privacy

    @property
    def enable_cache(self):
        return self._agent.context.config.enable_cache

    @enable_cache.setter
    def enable_cache(self, enable_cache: bool):
        self._agent.context.config.enable_cache = enable_cache
        if enable_cache:
            if self.cache is None:
                self._cache = Cache()
        else:
            self._cache = None

    @property
    def use_error_correction_framework(self):
        return self._agent.context.config.use_error_correction_framework

    @use_error_correction_framework.setter
    def use_error_correction_framework(self, use_error_correction_framework: bool):
        self._agent.context.config.use_error_correction_framework = (
            use_error_correction_framework
        )

    @property
    def custom_prompts(self):
        return self._agent.context.config.custom_prompts

    @custom_prompts.setter
    def custom_prompts(self, custom_prompts: dict):
        self._agent.context.config.custom_prompts = custom_prompts

    @property
    def save_charts(self):
        return self._agent.context.config.save_charts

    @save_charts.setter
    def save_charts(self, save_charts: bool):
        self._agent.context.config.save_charts = save_charts

    @property
    def save_charts_path(self):
        return self._agent.context.config.save_charts_path

    @save_charts_path.setter
    def save_charts_path(self, save_charts_path: str):
        self._agent.context.config.save_charts_path = save_charts_path

    @property
    def last_code_generated(self):
        return self._agent.last_code_generated

    @property
    def last_code_executed(self):
        return self._agent.last_code_executed

    @property
    def last_result(self):
        return self._agent.last_result

    @property
    def last_error(self):
        return self._agent.last_error

    @property
    def dfs(self):
        return self._agent.context.dfs

    @property
    def memory(self):
        return self._agent.context.memory

    @property
    def last_query_log_id(self):
        return self._agent.last_query_log_id
