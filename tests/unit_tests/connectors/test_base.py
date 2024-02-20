import pytest

from pandasai.connectors import BaseConnector
from pandasai.connectors.base import BaseConnectorConfig
from pandasai.helpers import Logger


class MockConfig:
    def __init__(self, host, port, database, table):
        self.host = host
        self.port = port
        self.database = database
        self.table = table


# Mock subclass of BaseConnector for testing
class MockConnector(BaseConnector):
    def _load_connector_config(self, config: BaseConnectorConfig):
        pass

    def _init_connection(self, config: BaseConnectorConfig):
        pass

    def head(self, n: int = 5):
        pass

    def execute(self):
        pass

    @property
    def rows_count(self):
        return 100

    @property
    def columns_count(self):
        return 5

    @property
    def column_hash(self):
        return "some_hash_value"

    @property
    def fallback_name(self):
        return "fallback_table_name"


# Mock Logger class for testing
class MockLogger(Logger):
    def __init__(self):
        pass


# Create a fixture for the configuration
@pytest.fixture
def mock_config():
    return MockConfig("localhost", 5432, "test_db", "test_table")


# Create a fixture for the connector with the configuration
@pytest.fixture
def mock_connector(mock_config):
    return MockConnector(mock_config)


def test_base_connector_initialization(mock_config, mock_connector):
    assert mock_connector.config == mock_config


def test_base_connector_path_property(mock_connector):
    expected_path = "MockConnector://localhost:5432/test_db/test_table"
    assert mock_connector.path == expected_path


def test_base_connector_logger_property(mock_connector):
    logger = MockLogger()
    mock_connector.logger = logger
    assert mock_connector.logger == logger


def test_base_connector_rows_count_property(mock_connector):
    assert mock_connector.rows_count == 100


def test_base_connector_columns_count_property(mock_connector):
    assert mock_connector.columns_count == 5


def test_base_connector_column_hash_property(mock_connector):
    assert mock_connector.column_hash == "some_hash_value"


def test_base_connector_fallback_name_property(mock_connector):
    assert mock_connector.fallback_name == "fallback_table_name"
