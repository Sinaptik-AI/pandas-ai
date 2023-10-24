from ..schemas.df_config import Config
from typing import Union, Optional, List
from pandasai.responses.context import Context
from ..helpers.logger import Logger
from pandasai.responses.response_parser import ResponseParser
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from pandasai import SmartDataframe


class BaseLogic(ABC):
    """
    Logic units for pipeline.
    """

    _config: Config = None
    _logger: Logger = None

    def __init__(self):
        pass

    @abstractmethod
    def call(self, config: Config, logger: Logger, input_):
        """
        This method will return output according to
        Implementation."""
        raise NotImplementedError("call method is not implemented.")


class PromptRequestLogic(BaseLogic):
    """
    Logic units for pipeline.
    """

    def __init__(
        self,
    ):
        super().__init__()

    def call(self, config: Config, logger: Logger, input_):
        """
        This method will return output according to
        implementation.
        """
        head = input_
        new_data = []
        column_data_types = head.dtypes

        ## generate 100 synthetic examples
        for _ in range(100):
            new_row = {}
            for column_name, data_type in column_data_types.iteritems():
                if np.issubdtype(data_type, np.number):
                    # Generate random numbers for numerical columns
                    mean = head[column_name].mean()
                    std_dev = head[column_name].std()
                    new_value = np.random.normal(mean, std_dev)
                else:
                    # Generate random values for non-numerical columns
                    unique_values = head[column_name].unique()
                    new_value = np.random.choice(unique_values)
                new_row[column_name] = new_value

            new_data.append(new_row)

        ## convert it into smartdataframe
        df = pd.DataFrame(new_data)
        return SmartDataframe(df, config=Config)


class Pipeline:
    """
    Base Pipeline class to be extended for other pipelines.
    """

    _config: Config = None
    _logger: Logger
    _logics: List[BaseLogic]

    def __init__(
        self,
        config: Union[Config, dict] = None,
        context: Optional[Context] = None,
        logics: Optional[List[BaseLogic]] = None,
        df: pd.DataFrame = None,
    ):
        """
        Intialize the pipeline with given context and configuration
            parameters.

        Args :
            context (Context) : Context is required for ResponseParsers.
            config (dict) : The configuration to pipeline.
        """

        if isinstance(config, dict):
            config = Config(**config)

        self._config = config

        self._logger = Logger(
            save_logs=self._config.save_logs, verbose=self._config.verbose
        )
        if not context:
            context = Context(self._config, self.logger, self.engine)

        if self._config.response_parser:
            self._response_parser = self._config.response_parser(context)
        else:
            self._response_parser = ResponseParser(context)

        self._logics = logics
        self._df = df

    @abstractmethod
    def execute(self):
        """
        This functions is responsible to loop through logic and
            Implementation.
        """
        result = self._df
        for logic in self._logics:
            result = logic.call(self._config, self._logger, result)

        return result
