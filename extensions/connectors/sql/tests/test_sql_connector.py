"""Unit tests for SQL connector"""

import pytest
from unittest.mock import MagicMock
from pandasai.agent import Agent
from pandasai.exceptions import InvalidConfigError


class TestSQLConnector:
    """Unit tests for SQL connector"""

    @pytest.fixture
    def sql_connector(self):
        mock_connector = MagicMock()
        mock_connector.type = "sql"
        mock_connector.get_table_names.return_value = ["table1", "table2"]
        return mock_connector

    @pytest.fixture
    def pgsql_connector(self):
        mock_connector = MagicMock()
        mock_connector.type = "postgresql"
        mock_connector.get_table_names.return_value = ["table3", "table4"]
        return mock_connector

    def test_validate_multiple_sql_connectors(self, sql_connector, pgsql_connector):
        """Test that agent raises an error when initialized with multiple SQL connectors"""
        llm = MagicMock()
        llm.type = "fake"

        with pytest.raises(InvalidConfigError):
            Agent(
                [sql_connector, pgsql_connector],
                {"llm": llm, "direct_sql": False},
                vectorstore=MagicMock(),
            )
