from unittest.mock import patch

import pandas as pd

from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema
from pandasai.data_loader.sql_loader import SQLDatasetLoader
from pandasai.dataframe.base import DataFrame


class TestVirtualDataFrameRowsCount:
    def test_rows_count_queries_the_source_once(self, mysql_schema):
        """rows_count issues a single COUNT(*) and serves later reads from cache."""
        loader = SQLDatasetLoader(mysql_schema, "test/users")

        with patch.object(
            SQLDatasetLoader, "execute_query", return_value=pd.DataFrame([[42]])
        ) as mock_execute_query:
            df = loader.load()

            assert df.rows_count == 42
            assert df.rows_count == 42
            assert df.rows_count == 42

            mock_execute_query.assert_called_once()

    def test_rows_count_is_not_shared_between_dataframes(self, mysql_schema):
        """Each VirtualDataFrame keeps its own count."""
        loader = SQLDatasetLoader(mysql_schema, "test/users")

        with patch.object(
            SQLDatasetLoader, "execute_query", return_value=pd.DataFrame([[7]])
        ) as mock_execute_query:
            first = loader.load()
            second = loader.load()

            assert first.rows_count == 7
            assert second.rows_count == 7

            assert mock_execute_query.call_count == 2

    def test_serialize_dataframe_does_not_re_query_the_row_count(self, mysql_schema):
        """Repeated prompt builds must not issue a COUNT(*) each time."""
        loader = SQLDatasetLoader(mysql_schema, "test/users")
        head = DataFrame(
            pd.DataFrame(
                {
                    "email": ["test@example.com"],
                    "first_name": ["John"],
                    "timestamp": [pd.Timestamp("2024-01-01")],
                }
            )
        )

        def execute_query(query, params=None):
            if "COUNT" in query.upper():
                return pd.DataFrame([[1000]])
            return head

        with patch.object(
            SQLDatasetLoader, "execute_query", side_effect=execute_query
        ) as mock_execute_query:
            df = loader.load()

            df.serialize_dataframe()
            df.serialize_dataframe()
            df.serialize_dataframe()

            count_queries = [
                call.args[0]
                for call in mock_execute_query.call_args_list
                if "COUNT" in call.args[0].upper()
            ]
            assert len(count_queries) == 1


class TestVirtualDataFrameColumnsCount:
    def test_columns_count_comes_from_the_schema(self, mysql_schema):
        """The backing frame is empty, so the schema supplies the column count."""
        loader = SQLDatasetLoader(mysql_schema, "test/users")

        with patch.object(
            SQLDatasetLoader, "execute_query", return_value=pd.DataFrame([[0]])
        ):
            df = loader.load()

            assert df.columns_count == 3

    def test_columns_count_falls_back_to_head_without_schema_columns(
        self, raw_mysql_schema
    ):
        """With no declared columns the cached head supplies the count."""
        raw_mysql_schema.pop("columns")
        raw_mysql_schema.pop("order_by")
        schema = SemanticLayerSchema(**raw_mysql_schema)
        loader = SQLDatasetLoader(schema, "test/users")

        head = DataFrame(pd.DataFrame({"email": ["a@b.com"], "first_name": ["John"]}))

        with patch.object(SQLDatasetLoader, "execute_query", return_value=head):
            df = loader.load()

            assert df.columns_count == 2

    def test_serialized_dimensions_report_both_axes(self, mysql_schema):
        """dimensions must carry the real column count, not the empty frame's."""
        loader = SQLDatasetLoader(mysql_schema, "test/users")
        head = DataFrame(
            pd.DataFrame(
                {
                    "email": ["test@example.com"],
                    "first_name": ["John"],
                    "timestamp": [pd.Timestamp("2024-01-01")],
                }
            )
        )

        def execute_query(query, params=None):
            if "COUNT" in query.upper():
                return pd.DataFrame([[98765432]])
            return head

        with patch.object(SQLDatasetLoader, "execute_query", side_effect=execute_query):
            df = loader.load()

            assert 'dimensions="98765432x3"' in df.serialize_dataframe()
