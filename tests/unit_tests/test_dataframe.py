import pytest
import pandas as pd
from pandasai import DataFrame
from pandasai.schemas.df_config import Config
from unittest.mock import patch, MagicMock
from pandasai.llm.fake import FakeLLM


@pytest.fixture
def sample_data():
    return {
        "Name": ["John", "Emma", "Liam", "Olivia", "Noah"],
        "Age": [28, 35, 22, 31, 40],
        "City": ["New York", "London", "Paris", "Tokyo", "Sydney"],
        "Salary": [75000, 82000, 60000, 79000, 88000],
    }


@pytest.fixture
def pandasai_df(sample_data):
    return DataFrame(sample_data)


def test_dataframe_initialization(sample_data, pandasai_df):
    assert isinstance(pandasai_df, DataFrame)
    assert isinstance(pandasai_df, pd.DataFrame)
    assert pandasai_df.equals(pd.DataFrame(sample_data))


def test_from_pandas(sample_data):
    pandas_df = pd.DataFrame(sample_data)
    pandasai_df = DataFrame.from_pandas(pandas_df)
    assert isinstance(pandasai_df, DataFrame)
    assert pandasai_df.equals(pandas_df)


@patch("pandasai.agent.Agent")
def test_chat_method(mock_agent, pandasai_df):
    mock_agent_instance = MagicMock()
    mock_agent_instance.chat.return_value = "Noah has the highest salary of 88000."
    mock_agent.return_value = mock_agent_instance

    result = pandasai_df.chat("Who has the highest salary?")

    # Use assert_called_once() instead of assert_called_once_with()
    mock_agent.assert_called_once()

    # Check if the Agent was called with the correct arguments
    args, kwargs = mock_agent.call_args
    assert len(args) == 1
    assert args[0] == [pandasai_df]
    assert isinstance(kwargs["config"], Config)

    # Additional assertions can be added here to check specific config properties if needed

    assert result == "Noah has the highest salary of 88000."


@patch("pandasai.agent.Agent")
def test_chat_method_with_custom_config(mock_agent, pandasai_df):
    mock_agent_instance = MagicMock()
    mock_agent_instance.chat.return_value = "Custom config response"
    mock_agent.return_value = mock_agent_instance

    config = Config(
        llm=FakeLLM(),
        verbose=True,
    )

    result = pandasai_df.chat("Custom config question", config=config)

    mock_agent.assert_called_once()
    called_config = mock_agent.call_args[1]["config"]
    assert called_config == config
    assert isinstance(called_config, Config)
    assert called_config.llm == config.llm
    assert called_config.verbose == config.verbose

    mock_agent_instance.chat.assert_called_once_with("Custom config question")
    assert result == "Custom config response"


def test_dataframe_operations(pandasai_df):
    # Test that standard pandas operations still work
    assert len(pandasai_df) == 5
    assert list(pandasai_df.columns) == ["Name", "Age", "City", "Salary"]
    assert pandasai_df["Salary"].mean() == 76800
