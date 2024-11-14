import pytest
import pandas as pd
from unittest.mock import Mock, patch
from pandasai.dataframe.base import DataFrame
from pandasai.agent.agent import Agent
import pandasai


class TestDataFrame:
    @pytest.fixture(autouse=True)
    def reset_current_agent(self):
        pandasai._current_agent = None
        yield
        pandasai._current_agent = None

    @pytest.fixture
    def sample_data(self):
        return {
            "Name": ["John", "Emma", "Liam", "Olivia", "Noah"],
            "Age": [28, 35, 22, 31, 40],
            "City": ["New York", "London", "Paris", "Tokyo", "Sydney"],
            "Salary": [75000, 82000, 60000, 79000, 88000],
        }

    @pytest.fixture
    def sample_df(self, sample_data):
        return DataFrame(sample_data)

    def test_dataframe_initialization(self, sample_data, sample_df):
        assert isinstance(sample_df, DataFrame)
        assert isinstance(sample_df, pd.DataFrame)
        assert sample_df.equals(pd.DataFrame(sample_data))

    def test_from_pandas(self, sample_data):
        pandas_df = pd.DataFrame(sample_data)
        pandasai_df = DataFrame.from_pandas(pandas_df)
        assert isinstance(pandasai_df, DataFrame)
        assert pandasai_df.equals(pandas_df)

    def test_dataframe_operations(self, sample_df):
        assert len(sample_df) == 5
        assert list(sample_df.columns) == ["Name", "Age", "City", "Salary"]
        assert sample_df["Salary"].mean() == 76800

    @patch("pandasai.agent.agent.Agent")
    def test_chat_creates_agent(self, mock_agent, sample_df):
        assert sample_df._agent is None
        sample_df.chat("Test query")
        mock_agent.assert_called_once_with([sample_df], config=sample_df.config)

    @patch("pandasai.Agent")
    def test_chat_reuses_existing_agent(self, sample_df):
        mock_agent = Mock(spec=Agent)
        sample_df._agent = mock_agent

        sample_df.chat("First query")
        assert sample_df._agent is not None
        initial_agent = sample_df._agent
        sample_df.chat("Second query")
        assert sample_df._agent is initial_agent

    def test_follow_up_without_chat_raises_error(self, sample_df):
        with pytest.raises(ValueError, match="No existing conversation"):
            sample_df.follow_up("Follow-up query")

    def test_follow_up_after_chat(self, sample_df):
        mock_agent = Mock(spec=Agent)
        sample_df._agent = mock_agent

        sample_df.follow_up("Follow-up query")
        assert mock_agent.follow_up.call_count == 1

    def test_chat_method(self, sample_df):
        mock_agent = Mock(spec=Agent)
        sample_df._agent = mock_agent

        sample_df.chat("Test question")

        assert sample_df._agent is not None
        assert mock_agent.chat.call_count == 1

    def test_chat_with_config(self, sample_df):
        config = {"max_retries": 100}
        with patch("pandasai.agent.agent.Agent") as mock_agent:
            sample_df.chat("Test query", config=config)
            mock_agent.assert_called_once_with([sample_df], config=sample_df.config)
        assert sample_df.config.max_retries == 100

    def test_column_hash(self, sample_df):
        assert hasattr(sample_df, "column_hash")
        assert isinstance(sample_df.column_hash, str)
        assert len(sample_df.column_hash) == 32  # MD5 hash length
