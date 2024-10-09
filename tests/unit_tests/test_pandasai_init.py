import pytest
from unittest.mock import patch, MagicMock
import pandasai
from pandasai.dataframe.base import DataFrame


class TestPandasAIInit:
    @pytest.fixture
    def sample_df(self):
        return DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    @pytest.fixture
    def sample_dataframes(self):
        df1 = DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        df2 = DataFrame({"X": [10, 20, 30], "Y": ["x", "y", "z"]})
        return [df1, df2]

    def test_chat_creates_agent(self, sample_df):
        with patch("pandasai.Agent") as MockAgent:
            pandasai.chat("Test query", sample_df)
            MockAgent.assert_called_once_with([sample_df])

    def test_chat_without_dataframes_raises_error(self):
        with pytest.raises(ValueError, match="At least one dataframe must be provided"):
            pandasai.chat("Test query")

    def test_follow_up_without_chat_raises_error(self):
        pandasai._current_agent = None

        with pytest.raises(ValueError, match="No existing conversation"):
            pandasai.follow_up("Follow-up query")

    def test_follow_up_after_chat(self, sample_df):
        with patch("pandasai.Agent") as MockAgent:
            mock_agent = MockAgent.return_value
            pandasai.chat("Test query", sample_df)
            pandasai.follow_up("Follow-up query")
            mock_agent.follow_up.assert_called_once_with("Follow-up query")

    def test_chat_with_multiple_dataframes(self, sample_dataframes):
        with patch("pandasai.Agent") as MockAgent:
            mock_agent_instance = MagicMock()
            MockAgent.return_value = mock_agent_instance
            mock_agent_instance.chat.return_value = "Mocked response"

            result = pandasai.chat("What is the sum of column A?", *sample_dataframes)

            MockAgent.assert_called_once_with(sample_dataframes)
            mock_agent_instance.chat.assert_called_once_with(
                "What is the sum of column A?"
            )
            assert result == "Mocked response"

    def test_chat_with_single_dataframe(self, sample_dataframes):
        with patch("pandasai.Agent") as MockAgent:
            mock_agent_instance = MagicMock()
            MockAgent.return_value = mock_agent_instance
            mock_agent_instance.chat.return_value = "Mocked response"

            result = pandasai.chat(
                "What is the average of column X?", sample_dataframes[1]
            )

            MockAgent.assert_called_once_with([sample_dataframes[1]])
            mock_agent_instance.chat.assert_called_once_with(
                "What is the average of column X?"
            )
            assert result == "Mocked response"
