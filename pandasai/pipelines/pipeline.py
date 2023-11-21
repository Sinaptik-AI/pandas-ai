import logging
from pandasai.config import load_config
from pandasai.exceptions import UnSupportedLogicUnit
from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.logger import Logger
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from ..schemas.df_config import Config
from typing import Any, Optional, List, Union
from .abstract_pipeline import AbstractPipeline


class Pipeline(AbstractPipeline):
    """
    Base Pipeline class to be used to create custom pipelines
    """

    _context: PipelineContext
    _logger: Logger
    _steps: List[BaseLogicUnit]

    def __init__(
        self,
        context: Union[List[Union[DataFrameType, Any]], PipelineContext] = None,
        config: Optional[Union[Config, dict]] = None,
        steps: Optional[List] = None,
        logger: Optional[Logger] = None,
    ):
        """
        Initialize the pipeline with given context and configuration
            parameters.
        Args :
            context (Context) : Context is required for ResponseParsers.
            config (dict) : The configuration to pipeline.
            steps: (list): List of logic Units
            logger: (Logger): logger
        """

        if not isinstance(context, PipelineContext):
            from pandasai.smart_dataframe import load_smartdataframes

            config = Config(**load_config(config))
            smart_dfs = load_smartdataframes(context, config)
            context = PipelineContext(smart_dfs, config)

        self._logger = (
            Logger(save_logs=context.config.save_logs, verbose=context.config.verbose)
            if logger is None
            else logger
        )

        self._context = context
        self._steps = steps or []

    def add_step(self, logic: BaseLogicUnit):
        """
        Adds new logics in the pipeline
        Args:
            logic (BaseLogicUnit): execution unit of logic
        """
        if not isinstance(logic, BaseLogicUnit):
            raise UnSupportedLogicUnit(
                "Logic unit must be inherited from BaseLogicUnit and "
                "must implement execute method"
            )

        self._steps.append(logic)

    def run(self, data: Any = None) -> Any:
        """
        This functions is responsible to loop through logics
        Args:
            data (Any, optional): Input Data to run the pipeline. Defaults to None.

        Returns:
            Any: Depends on the type can return anything
        """
        try:
            for index, logic in enumerate(self._steps):
                self._logger.log(f"Executing Step {index}: {logic.__class__.__name__}")

                if logic.skip_if is not None and logic.skip_if(self._context):
                    continue

                data = logic.execute(
                    data,
                    logger=self._logger,
                    config=self._context.config,
                    context=self._context,
                )

        except Exception as e:
            self._logger.log(f"Pipeline failed on step {index}: {e}", logging.ERROR)
            raise e

        return data
