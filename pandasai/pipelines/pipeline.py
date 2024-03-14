import logging
import time
from typing import Any, List, Optional, Union

from pandasai.config import load_config_from_json
from pandasai.exceptions import UnSupportedLogicUnit
from pandasai.helpers.logger import Logger
from pandasai.helpers.query_exec_tracker import QueryExecTracker
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.pipeline_context import PipelineContext

from ..connectors import BaseConnector
from ..schemas.df_config import Config
from .abstract_pipeline import AbstractPipeline


class Pipeline(AbstractPipeline):
    """
    Base Pipeline class to be used to create custom pipelines
    """

    _context: PipelineContext
    _logger: Logger
    _steps: List[BaseLogicUnit]
    _query_exec_tracker: Optional[QueryExecTracker]

    def __init__(
        self,
        context: Union[List[BaseConnector], PipelineContext],
        config: Optional[Union[Config, dict]] = None,
        query_exec_tracker: Optional[QueryExecTracker] = None,
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
            config = Config(**load_config_from_json(config))
            connectors = context
            context = PipelineContext(connectors, config)

        self._logger = (
            Logger(save_logs=context.config.save_logs, verbose=context.config.verbose)
            if logger is None
            else logger
        )

        self._context = context

        if steps:
            for i in range(len(steps) - 1):
                steps[i].next_step = steps[i + 1]

        self._steps = steps or []
        self._query_exec_tracker = query_exec_tracker or QueryExecTracker(
            server_config=self._context.config.log_server
        )

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

        if self._steps:
            self._steps[-1].next_step = logic

        self._steps.append(logic)

    def run(self, data: Any = None) -> Any:
        """
        This functions is responsible to loop through logics
        Args:
            data (Any, optional): Input Data to run the pipeline. Defaults to None.

        Returns:
            Any: Depends on the type can return anything
        """
        if not self._steps:
            return data

        try:
            logic = self._steps[0]
            while logic:
                step_name = logic.__class__.__name__

                # Callback function before execution
                if logic.before_execution is not None:
                    logic.before_execution(data)

                self._logger.log(f"Executing {step_name} step")

                if logic.skip_if is not None and logic.skip_if(self._context):
                    self._logger.log(f"Skipping {step_name} step...")
                    logic = logic.next_step
                    continue

                start_time = time.time()

                # Execute the logic unit
                step_output = logic.execute(
                    data,
                    logger=self._logger,
                    config=self._context.config,
                    context=self._context,
                )

                execution_time = time.time() - start_time

                # Track the execution step of pipeline
                if isinstance(step_output, LogicUnitOutput):
                    self._query_exec_tracker.add_step(
                        {
                            "type": logic.__class__.__name__,
                            "success": step_output.success,
                            "message": step_output.message,
                            "execution_time": execution_time,
                            "data": step_output.metadata,
                        }
                    )

                    if step_output.final_track_output:
                        self._query_exec_tracker.set_final_response(
                            step_output.metadata
                        )

                    data = step_output.output
                else:
                    data = step_output

                # Callback function after execution
                if logic.on_execution is not None:
                    logic.on_execution(data)

                logic = logic.next_step

        except Exception as e:
            self._logger.log(f"Pipeline failed on {step_name} step: {e}", logging.ERROR)
            raise e

        return data

    def __or__(self, pipeline: "Pipeline") -> Any:
        """
        This functions is responsible to pipe two pipelines
        Args:
            pipeline (Pipeline): Second Pipeline which will be Piped to the self.
            data (Any, optional): Input Data to run the pipeline. Defaults to None.

        Returns:
            Any: Depends on the type can return anything
        """

        combined_pipeline = Pipeline(
            context=self._context,
            logger=self._logger,
            query_exec_tracker=self._query_exec_tracker,
        )

        for step in self._steps:
            combined_pipeline.add_step(step)

        for step in pipeline._steps:
            combined_pipeline.add_step(step)

        return combined_pipeline
