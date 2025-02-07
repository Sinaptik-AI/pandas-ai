import pytest

from pandasai.query_builders.sql_parser import SQLParser


class TestSqlParser:
    @staticmethod
    @pytest.mark.parametrize(
        "query, table_mapping, expected",
        [
            (
                "SELECT * FROM customers",
                {"customers": "clients"},
                """SELECT
  *
FROM "clients" AS customers""",
            ),
            (
                "SELECT * FROM orders",
                {"orders": "(SELECT * FROM sales)"},
                """SELECT
  *
FROM (
  (
    SELECT
      *
    FROM "sales"
  )
) AS orders""",
            ),
            (
                "SELECT * FROM customers c",
                {"customers": "clients"},
                """SELECT
  *
FROM "clients" AS c""",
            ),
            (
                "SELECT c.id, o.amount FROM customers c JOIN orders o ON c.id = o.customer_id",
                {"customers": "clients", "orders": "(SELECT * FROM sales)"},
                '''SELECT
  "c"."id",
  "o"."amount"
FROM "clients" AS c
JOIN (
  (
    SELECT
      *
    FROM "sales"
  )
) AS o
  ON "c"."id" = "o"."customer_id"''',
            ),
        ],
    )
    def test_replace_table_names(query, table_mapping, expected):
        result = SQLParser.replace_table_and_column_names(query, table_mapping)
        assert result.strip() == expected.strip()
