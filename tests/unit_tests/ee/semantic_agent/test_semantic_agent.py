from unittest.mock import MagicMock, patch, PropertyMock

import pandasai as pai
import pandas as pd
import pytest
import os

from pandasai.agent import Agent
from pandasai.agent.base import BaseAgent
from pandasai.ee.agents.semantic_agent import SemanticAgent
from pandasai.exceptions import InvalidTrainJson
from pandasai.llm.fake import FakeLLM
from tests.unit_tests.ee.helpers.schema import (
    VIZ_QUERY_SCHEMA,
    VIZ_QUERY_SCHEMA_STR,
)
from pandasai.dataframe.base import DataFrame


class TestSemanticAgent:
    "Unit tests for Agent class"

    @pytest.fixture
    def sample_df(self):
        df = pai.DataFrame(
            {
                "order_id": [10248, 10249, 10250],
                "customer_id": ["VINET", "TOMSP", "HANAR"],
                "employee_id": [5, 6, 4],
                "order_date": pd.to_datetime(
                    ["1996-07-04", "1996-07-05", "1996-07-08"]
                ),
                "required_date": pd.to_datetime(
                    ["1996-08-01", "1996-08-16", "1996-08-05"]
                ),
                "shipped_date": pd.to_datetime(
                    ["1996-07-16", "1996-07-10", "1996-07-12"]
                ),
                "ship_via": [3, 1, 2],
                "freight": [32.38, 11.61, 65.83],
                "ship_name": [
                    "Vins et alcools Chevalier",
                    "Toms Spezialitäten",
                    "Hanari Carnes",
                ],
                "ship_address": [
                    "59 rue de l'Abbaye",
                    "Luisenstr. 48",
                    "Rua do Paço, 67",
                ],
                "ship_city": ["Reims", "Münster", "Rio de Janeiro"],
                "ship_region": ["CJ", None, "RJ"],
                "ship_postal_code": ["51100", "44087", "05454-876"],
                "ship_country": ["France", "Germany", "Brazil"],
            }
        )
        return DataFrame(df)

    @pytest.fixture
    def llm(self) -> FakeLLM:
        return FakeLLM(output=VIZ_QUERY_SCHEMA_STR)

    @pytest.fixture
    def agent(self, sample_df: DataFrame, llm: FakeLLM) -> Agent:
        with patch.dict(os.environ, {"PANDASAI_API_KEY": "test_key"}), patch(
            "pandasai.ee.agents.semantic_agent.SemanticAgent._create_schema"
        ) as mock_create_schema:
            mock_create_schema.return_value = None
            return SemanticAgent(
                sample_df, config={"llm": llm}, vectorstore=MagicMock()
            )

    def test_base_agent_construct(self, sample_df, llm):
        BaseAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())

    def test_base_agent_log_id_register_agent(self, sample_df, llm):
        with patch.dict(os.environ, {"PANDASAI_API_KEY": "test_key"}), patch(
            "pandasai.ee.agents.semantic_agent.SemanticAgent._create_schema"
        ) as mock_create_schema, patch("uuid.uuid4") as mock_uuid:
            mock_create_schema.return_value = None
            mock_uuid.return_value = "test-uuid"
            agent = SemanticAgent(
                sample_df, {"llm": llm, "enable_cache": False}, vectorstore=MagicMock()
            )
            agent.context.config.__dict__["log_id"] = "test-uuid"
            assert agent.context.config.__dict__["log_id"] == "test-uuid"

    def test_constructor_with_no_bamboo(self, sample_df):
        non_bamboo_llm = FakeLLM(output=VIZ_QUERY_SCHEMA_STR, type="fake")
        with pytest.raises(Exception):
            SemanticAgent(
                sample_df,
                {"llm": non_bamboo_llm, "enable_cache": False},
                vectorstore=MagicMock(),
            )

    def test_constructor(self, sample_df, llm):
        with patch.dict(os.environ, {"PANDASAI_API_KEY": "test_key"}), patch(
            "pandasai.ee.agents.semantic_agent.SemanticAgent._create_schema"
        ) as mock_create_schema:
            mock_create_schema.return_value = None
            agent = SemanticAgent(
                sample_df, {"llm": llm, "enable_cache": False}, vectorstore=MagicMock()
            )
            assert agent.context.config.llm == llm

    def test_last_error(self, sample_df, llm):
        with patch.dict(os.environ, {"PANDASAI_API_KEY": "test_key"}), patch(
            "pandasai.ee.agents.semantic_agent.SemanticAgent._create_schema"
        ) as mock_create_schema, patch.object(
            BaseAgent, "last_error", new_callable=PropertyMock
        ) as mock_last_error:
            mock_create_schema.return_value = None
            mock_last_error.return_value = None
            agent = SemanticAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())
            assert agent.last_error is None

    @patch("pandasai.helpers.cache.Cache.get")
    def test_cache_of_schema(self, mock_cache_get, sample_df, llm):
        mock_cache_get.return_value = VIZ_QUERY_SCHEMA_STR

        agent = SemanticAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())

        assert not llm.called
        assert agent._schema == VIZ_QUERY_SCHEMA

    def test_train_method_with_qa(self, agent):
        queries = ["query1"]
        jsons = ['{"name": "test"}']
        agent.train(queries=queries, jsons=jsons)

        agent._vectorstore.add_docs.assert_not_called()
        agent._vectorstore.add_question_answer.assert_called_once_with(queries, jsons)

    def test_train_method_with_docs(self, agent):
        docs = ["doc1"]
        agent.train(docs=docs)

        agent._vectorstore.add_question_answer.assert_not_called()
        agent._vectorstore.add_docs.assert_called_once()
        agent._vectorstore.add_docs.assert_called_once_with(docs)

    def test_train_method_with_docs_and_qa(self, agent):
        docs = ["doc1"]
        queries = ["query1"]
        jsons = ['{"name": "test"}']
        agent.train(queries, jsons, docs=docs)

        agent._vectorstore.add_question_answer.assert_called_once()
        agent._vectorstore.add_question_answer.assert_called_once_with(queries, jsons)
        agent._vectorstore.add_docs.assert_called_once()
        agent._vectorstore.add_docs.assert_called_once_with(docs)

    def test_train_method_with_queries_but_no_code(self, agent):
        queries = ["query1", "query2"]
        with pytest.raises(ValueError):
            agent.train(queries)

    def test_train_method_with_code_but_no_queries(self, agent):
        jsons = ["code1", "code2"]
        with pytest.raises(InvalidTrainJson):
            agent.train(jsons=jsons)
