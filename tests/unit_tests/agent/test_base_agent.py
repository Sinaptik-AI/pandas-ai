import pytest
import pandas as pd
from unittest.mock import Mock, patch
from pandasai.agent.base import BaseAgent
from pandasai.pipelines.chat.chat_pipeline_input import ChatPipelineInput
from pandasai.connectors import PandasConnector


class TestBaseAgent:
    @pytest.fixture
    def mock_agent(self):
        # Create a mock DataFrame
        mock_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

        # Create a PandasConnector with the mock DataFrame
        mock_connector = PandasConnector({"original_df": mock_df})

        # Create the BaseAgent with the mock connector
        with patch("pandasai.agent.base.PandasConnector", return_value=mock_connector):
            agent = BaseAgent([mock_df])

        agent.pipeline = Mock()
        agent.context = Mock()
        agent.context.config.llm.type = "test_llm"
        agent.logger = Mock()
        return agent

    def test_chat_starts_new_conversation(self, mock_agent):
        with patch.object(mock_agent, "start_new_conversation") as mock_start_new:
            mock_agent.chat("Test query")
            mock_start_new.assert_called_once()

    def test_follow_up_continues_conversation(self, mock_agent):
        with patch.object(mock_agent, "start_new_conversation") as mock_start_new:
            mock_agent.follow_up("Follow-up query")
            mock_start_new.assert_not_called()

    def test_chat_and_follow_up_use_process_query(self, mock_agent):
        with patch.object(mock_agent, "_process_query") as mock_process:
            mock_agent.chat("Test query")
            mock_process.assert_called_once_with("Test query", None)

            mock_process.reset_mock()

            mock_agent.follow_up("Follow-up query")
            mock_process.assert_called_once_with("Follow-up query", None)

    def test_process_query_calls_pipeline(self, mock_agent):
        mock_agent._process_query("Test query")
        mock_agent.pipeline.run.assert_called_once()
        assert isinstance(mock_agent.pipeline.run.call_args[0][0], ChatPipelineInput)

    def test_process_query_handles_exceptions(self, mock_agent):
        mock_agent.pipeline.run.side_effect = Exception("Test error")
        result = mock_agent._process_query("Test query")
        assert "Test error" in result

    def test_malicious_query_detection(self, mock_agent):
        result = mock_agent._process_query("import os; os.system('rm -rf /')")
        assert (
            "The query contains references to io or os modules or b64decode method which can be used to execute or access system resources in unsafe ways."
            in result
        )
