import pandasai as pai
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def sample_dataframes():
    df1 = pai.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
    df2 = pai.DataFrame({"X": [10, 20, 30], "Y": ["x", "y", "z"]})
    return [df1, df2]


def test_chat_with_multiple_dataframes(sample_dataframes):
    with patch("pandasai.Agent") as MockAgent:
        mock_agent_instance = MagicMock()
        MockAgent.return_value = mock_agent_instance
        mock_agent_instance.chat.return_value = "Mocked response"

        result = pai.chat("What is the sum of column A?", *sample_dataframes)

        MockAgent.assert_called_once_with(sample_dataframes)
        mock_agent_instance.chat.assert_called_once_with("What is the sum of column A?")
        assert result == "Mocked response"


def test_chat_with_single_dataframe(sample_dataframes):
    with patch("pandasai.Agent") as MockAgent:
        mock_agent_instance = MagicMock()
        MockAgent.return_value = mock_agent_instance
        mock_agent_instance.chat.return_value = "Mocked response"

        result = pai.chat("What is the average of column X?", sample_dataframes[1])

        MockAgent.assert_called_once_with([sample_dataframes[1]])
        mock_agent_instance.chat.assert_called_once_with(
            "What is the average of column X?"
        )
        assert result == "Mocked response"


def test_chat_with_no_dataframes():
    with pytest.raises(ValueError, match="At least one dataframe must be provided."):
        pai.chat("This should raise an error")
