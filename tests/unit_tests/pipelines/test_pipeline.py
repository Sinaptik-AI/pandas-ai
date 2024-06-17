from typing import Any, Optional
from unittest.mock import Mock

import pandas as pd
import pytest

from pandasai.connectors import BaseConnector, PandasConnector
from pandasai.ee.agents.judge_agent import JudgeAgent
from pandasai.helpers.logger import Logger
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.schemas.df_config import Config


class MockLogicUnit(BaseLogicUnit):
    def execute(self, input: Any, **kwargs) -> Any:
        pass


class TestPipeline:
    @pytest.fixture
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

    @pytest.fixture
    def dataframe(self, sample_df):
        return PandasConnector({"original_df": sample_df})

    @pytest.fixture
    def config(self, llm):
        return {"llm": llm, "enable_cache": False}

    @pytest.fixture
    def context(self, sample_df, config):
        return PipelineContext([sample_df], config)

    @pytest.fixture
    def logger(self):
        return Logger(True, False)

    def test_init(self, context, config):
        # Test the initialization of the Pipeline
        pipeline = Pipeline(context)
        assert isinstance(pipeline, Pipeline)
        assert pipeline._context.config == Config(**config)
        assert pipeline._context == context
        assert pipeline._steps == []

    def test_init_with_agent(self, dataframe, config):
        # Test the initialization of the Pipeline
        pipeline = Pipeline([dataframe], config=config)
        assert isinstance(pipeline, Pipeline)
        assert len(pipeline._context.dfs) == 1
        assert isinstance(pipeline._context.dfs[0], BaseConnector)

    def test_init_with_dfs(self, dataframe, config):
        # Test the initialization of the Pipeline
        pipeline = Pipeline([dataframe], config=config)
        assert isinstance(pipeline, Pipeline)
        assert len(pipeline._context.dfs) == 1
        assert isinstance(pipeline._context.dfs[0], BaseConnector)

    def test_add_step(self, context, config):
        # Test the add_step method
        pipeline = Pipeline(context, config=config)
        logic_unit = MockLogicUnit()
        pipeline.add_step(logic_unit)
        assert len(pipeline._steps) == 1
        assert pipeline._steps[0] == logic_unit

    def test_add_step_using_constructor(self, context, config):
        logic_unit = MockLogicUnit()
        pipeline = Pipeline(context, steps=[logic_unit])
        assert len(pipeline._steps) == 1
        assert pipeline._steps[0] == logic_unit

    def test_add_step_unknown_logic_unit(self, context, config):
        pipeline = Pipeline(context)
        with pytest.raises(Exception):
            pipeline.add_step(Mock())

    def test_run(self, context, config):
        # Test the run method
        pipeline = Pipeline(context)

        class MockLogicUnit(BaseLogicUnit):
            def execute(self, data, logger, config, context):
                return "MockData"

        pipeline.add_step(MockLogicUnit())
        result = pipeline.run("InitialData")
        assert result == "MockData"

    def test_run_with_exception(self, context, config):
        # Test the run method with a mock logic unit that raises an exception
        pipeline = Pipeline(context)

        class MockLogicUnit(BaseLogicUnit):
            def execute(self, data, logger, config, context):
                raise Exception("Mock exception")

        pipeline.add_step(MockLogicUnit())
        with pytest.raises(Exception):
            pipeline.run("InitialData")

    def test_run_with_empty_pipeline(self, context, config):
        pipeline_3 = Pipeline(context, [])
        result = pipeline_3.run(5)
        assert result == 5

    def test_run_with_multiple_steps(self, context, config):
        class MockLogic(BaseLogicUnit):
            def execute(self, data, logger, config, context):
                return data + 1

        pipeline_2 = Pipeline(context, steps=[MockLogic(), MockLogic(), MockLogic()])

        result = pipeline_2.run(5)
        assert result == 8

    def test_pipeline_constructor_with_judge(self, context):
        judge_agent = JudgeAgent()
        pipeline = GenerateChatPipeline(context=context, judge=judge_agent)
        assert pipeline.judge == judge_agent
        assert isinstance(pipeline.context, PipelineContext)

    def test_pipeline_constructor_with_no_judge(self, context):
        judge_agent = JudgeAgent()
        pipeline = GenerateChatPipeline(context=context, judge=judge_agent)
        assert pipeline.judge == judge_agent
        assert isinstance(pipeline.context, PipelineContext)
