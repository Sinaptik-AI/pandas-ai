import pytest

from pandasai.exceptions import MaliciousQueryError
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
            (
                """SELECT d.name AS department, hse.name AS employee, hse.salary
FROM (
    SELECT * FROM employees WHERE salary > 50000
) AS hse
JOIN departments d ON hse.dept_id = d.id;
""",
                {"employees": "employee", "departments": "department"},
                """SELECT
  "d"."name" AS "department",
  "hse"."name" AS "employee",
  "hse"."salary"
FROM (
  SELECT
    *
  FROM "employee" AS employees
  WHERE
    "salary" > 50000
) AS "hse"
JOIN "department" AS d
  ON "hse"."dept_id" = "d"."id"
""",
            ),
        ],
    )
    def test_replace_table_names(query, table_mapping, expected):
        result = SQLParser.replace_table_and_column_names(query, table_mapping)
        assert result.strip() == expected.strip()

    def test_mysql_transpilation(self):
        query = '''SELECT COUNT(*) AS "total_rows"'''
        expected = """SELECT\n  COUNT(*) AS `total_rows`"""
        result = SQLParser.transpile_sql_dialect(query, to_dialect="mysql")
        assert result.strip() == expected.strip()

    @staticmethod
    @pytest.mark.parametrize(
        "sql_query, dialect, expected_tables",
        [
            # 1. Simple SELECT query
            ("SELECT * FROM users;", "postgres", ["users"]),
            # 2. Query with INNER JOIN
            (
                "SELECT * FROM users u JOIN orders o ON u.id = o.user_id;",
                "postgres",
                ["users", "orders"],
            ),
            # 3. Query with LEFT JOIN
            (
                "SELECT * FROM customers c LEFT JOIN orders o ON c.id = o.customer_id;",
                "postgres",
                ["customers", "orders"],
            ),
            # 4. Subquery
            (
                "SELECT * FROM (SELECT * FROM employees) AS e;",
                "postgres",
                ["employees"],
            ),
            # 5. CTE (Common Table Expression)
            (
                """
    WITH sales_data AS (SELECT * FROM sales)
    SELECT * FROM sales_data;
    """,
                "postgres",
                ["sales"],
            ),
            # 6. Table with alias (should return original table name)
            ("SELECT u.name FROM users AS u;", "postgres", ["users"]),
            # 7. Schema-prefixed table
            ("SELECT * FROM sales.customers;", "postgres", ["customers"]),
            # 8. Quoted table names (double quotes for PostgreSQL, backticks for MySQL)
            ('SELECT * FROM "Order Details";', "postgres", ["Order Details"]),
            # ("SELECT * FROM `Order Details`;", "mysql", ["Order Details"]),
            # 11. Edge Case: Invalid Query (should return empty list instead of raising an error)
            ("SELECT *", "postgres", []),
        ],
    )
    def test_extract_table_names(sql_query, dialect, expected_tables):
        result = SQLParser.extract_table_names(sql_query, dialect)
        assert SQLParser.extract_table_names(sql_query, dialect) == expected_tables
