from unittest.mock import Mock

import pandas as pd
import pytest

from pandasai.config import Config
from pandasai.smart_datalake import SmartDatalake


@pytest.fixture
def sample_dataframes():
    df1 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    df2 = pd.DataFrame({"C": [7, 8, 9], "D": [10, 11, 12]})
    return [df1, df2]


def test_dfs_property(sample_dataframes):
    # Create a mock agent with context
    mock_agent = Mock()
    mock_agent.context.dfs = sample_dataframes

    # Create SmartDatalake instance
    smart_datalake = SmartDatalake(sample_dataframes)
    smart_datalake._agent = mock_agent  # Inject mock agent

    # Test that dfs property returns the correct dataframes
    assert smart_datalake.dfs == sample_dataframes


def test_enable_cache(sample_dataframes):
    # Create a mock agent with context and config
    mock_config = Config(enable_cache=True)
    mock_agent = Mock()
    mock_agent.context.config = mock_config

    # Create SmartDatalake instance
    smart_datalake = SmartDatalake(sample_dataframes)
    smart_datalake._agent = mock_agent  # Inject mock agent

    # Test that enable_cache property returns the correct value
    assert smart_datalake.enable_cache is True

    # Test with cache disabled
    mock_config.enable_cache = False
    assert smart_datalake.enable_cache is False
