import pytest

from pandasai.data_loader.duck_db_connection_manager import DuckDBConnectionManager


class TestDuckDBConnectionManager:
    @pytest.fixture
    def duck_db_manager(self):
        return DuckDBConnectionManager()

    def test_connection_correct_closing_doesnt_throw(self, duck_db_manager):
        duck_db_manager.close()
