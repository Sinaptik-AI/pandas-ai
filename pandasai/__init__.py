# -*- coding: utf-8 -*-
"""
PandasAI is a wrapper around a LLM to make dataframes conversational

This module includes the implementation of basis  PandasAI class with methods to run
the LLMs models on Pandas dataframes. Following LLMs are implemented so far.

Example:

    This module is the Entry point of the `pandasai` package. Following is an example
    of how to use this Class.

    ```python
    import pandas as pd
    from pandasai import PandasAI

    # Sample DataFrame
    df = pd.DataFrame({
        "country": ["United States", "United Kingdom", "France", "Germany", "Italy",
        "Spain", "Canada", "Australia", "Japan", "China"],
        "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832,
        1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440,
        14631844184064],
        "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
    })

    # Instantiate a LLM
    from pandasai.llm.openai import OpenAI
    llm = OpenAI(api_token="YOUR_API_TOKEN")

    pandas_ai = PandasAI(llm)
    pandas_ai(df, prompt='Which are the 5 happiest countries?')

    ```
"""
import warnings
from typing import List, Optional, Union, Dict, Type
import importlib.metadata

import pandas as pd
from .smart_dataframe import SmartDataframe
from .smart_datalake import SmartDatalake
from .prompts.base import AbstractPrompt
from .callbacks.base import BaseCallback
from .schemas.df_config import Config
from .helpers.cache import Cache
from .agent import Agent

__version__ = importlib.metadata.version(__package__ or __name__)


class PandasAI:
    """
    PandasAI is a wrapper around a LLM to make dataframes conversational.


    This is an entry point of `pandasai` object. This class consists of methods
    to interface the LLMs with Pandas     dataframes. A pandas dataframe metadata i.e.
    df.head() and prompt is passed on to chosen LLMs API end point to generate a Python
    code to answer the questions asked. The resultant python code is run on actual data
    and answer is converted into a conversational form.

    Note:
        Do not include the `self` parameter in the ``Args`` section.
    Args:
        _llm (obj): LLMs option to be used for API access
        _verbose (bool, optional): To show the intermediate outputs e.g. python code
        generated and execution step on the prompt. Default to False
        _enforce_privacy (bool, optional): Do not display the data on prompt in case of
        Sensitive data. Default to False
        _max_retries (int, optional): max no. of tries to generate code on failure.
        Default to 3
        _original_instructions (dict, optional): The dict of instruction to run. Default
        to None
        _cache (Cache, optional): Cache object to store the results. Default to None
        _enable_cache (bool, optional): Whether to enable cache. Default to True
        _logger (logging.Logger, optional): Logger object to log the messages. Default
        to None
        _logs (List[dict], optional): List of logs to be stored. Default to []
        _prompt_id (str, optional): Unique ID to differentiate calls. Default to None
        _middlewares (List[Middleware], optional): List of middlewares to run. Default
        to [ChartsMiddleware()]
        _additional_dependencies (List[dict], optional): List of additional dependencies
        to be added. Default to []
        _custom_whitelisted_dependencies (List[str], optional): List of custom
        whitelisted dependencies. Default to []
        last_code_generated (str, optional): Pass last Code if generated. Default to
        None
        last_code_executed (str, optional): Pass the last execution / run. Default to
        None
        code_output (str, optional): The code output if any. Default to None
        last_error (str, optional): Error of running code last time. Default to None
        prompt_id (str, optional): Unique ID to differentiate calls. Default to None


    Returns (str): Response to a Question related to Data

    """

    _dl: SmartDatalake = None
    _config: Union[Config, dict]

    def __init__(
        self,
        llm=None,
        conversational=False,
        verbose=False,
        enforce_privacy=False,
        save_charts=False,
        save_charts_path="",
        enable_cache=True,
        middlewares=None,
        custom_whitelisted_dependencies=None,
        enable_logging=True,
        non_default_prompts: Optional[Dict[str, Type[AbstractPrompt]]] = None,
        callback: Optional[BaseCallback] = None,
    ):
        """
        __init__ method of the Class PandasAI

        Args:
            llm (object): LLMs option to be used for API access. Default is None
            conversational (bool): Whether to return answer in conversational form.
            Default to False
            verbose (bool): To show the intermediate outputs e.g. python code
            generated and execution step on the prompt.  Default to False
            enforce_privacy (bool): Execute the codes with Privacy Mode ON.
            Default to False
            save_charts (bool): Save the charts generated in the notebook.
            Default to False
            enable_cache (bool): Enable the cache to store the results.
            Default to True
            middlewares (list): List of middlewares to be used. Default to None
            custom_whitelisted_dependencies (list): List of custom dependencies to
            be used. Default to None
            enable_logging (bool): Enable the logging. Default to True
            non_default_prompts (dict): Mapping from keys to replacement prompt classes.
            Used to override specific types of prompts. Defaults to None.
        """

        # configure the logging
        # noinspection PyArgumentList
        # https://stackoverflow.com/questions/61226587/pycharm-does-not-recognize-logging-basicconfig-handlers-argument

        warnings.warn(
            "`PandasAI` (class) is deprecated since v1.0 and will be removed "
            "in a future release. Please use `SmartDataframe` instead."
        )

        self._config = Config(
            conversational=conversational,
            verbose=verbose,
            enforce_privacy=enforce_privacy,
            save_charts=save_charts,
            save_charts_path=save_charts_path,
            enable_cache=enable_cache,
            middlewares=middlewares or [],
            custom_whitelisted_dependencies=custom_whitelisted_dependencies or [],
            enable_logging=enable_logging,
            non_default_prompts=non_default_prompts,
            llm=llm,
            callback=callback,
        )

    def run(
        self,
        data_frame: Union[pd.DataFrame, List[pd.DataFrame]],
        prompt: str,
        show_code: bool = False,
        anonymize_df: bool = True,
        use_error_correction_framework: bool = True,
    ) -> Union[str, pd.DataFrame]:
        """
        Run the PandasAI to make Dataframes Conversational.

        Args:
            data_frame (Union[pd.DataFrame, List[pd.DataFrame]]): A pandas Dataframe
            prompt (str): A prompt to query about the Dataframe
            show_code (bool): To show the intermediate python code generated on the
            prompt. Default to False
            anonymize_df (bool): Running the code with Sensitive Data. Default to True
            use_error_correction_framework (bool): Turn on Error Correction mechanism.
            Default to True

        Returns (str): Answer to the Input Questions about the DataFrame

        """

        new_config = self._config.dict()
        new_config["show_code"] = show_code
        new_config["anonymize_df"] = anonymize_df
        new_config["use_error_correction_framework"] = use_error_correction_framework

        config = Config(**new_config).dict()

        if not isinstance(data_frame, list):
            data_frame = [data_frame]

        self._dl = SmartDatalake(data_frame, config)
        return self._dl.chat(prompt)

    def __call__(
        self,
        data_frame: Union[pd.DataFrame, List[pd.DataFrame]],
        prompt: str,
        show_code: bool = False,
        anonymize_df: bool = True,
        use_error_correction_framework: bool = True,
    ) -> Union[str, pd.DataFrame]:
        """
        __call__ method of PandasAI class. It calls the `run` method.

        Args:
            data_frame:
            prompt:
            show_code:
            anonymize_df:
            use_error_correction_framework:

        Returns (str): Answer to the Input Questions about the DataFrame.

        """

        return self.run(
            data_frame,
            prompt,
            show_code,
            anonymize_df,
            use_error_correction_framework,
        )

    @property
    def logs(self) -> List[dict[str, str]]:
        """Return the logs"""
        if self._dl is None:
            return []
        return self._dl.logs

    @property
    def last_prompt_id(self) -> str:
        """Return the id of the last prompt that was run."""
        if self._dl is None:
            return None
        return self._dl.last_prompt_id

    @property
    def last_prompt(self) -> str:
        """Return the last prompt that was executed."""
        if self._dl is None:
            return None
        return self._dl.last_prompt


def clear_cache(filename: str = None):
    """Clear the cache"""
    cache = Cache(filename or "cache_db")
    cache.clear()


__all__ = ["PandasAI", "SmartDataframe", "SmartDatalake", "Agent", "clear_cache"]
