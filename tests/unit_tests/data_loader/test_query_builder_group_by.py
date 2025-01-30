import pytest

from pandasai.data_loader.query_builder import QueryBuilder
from pandasai.data_loader.semantic_layer_schema import (
    Column,
    SemanticLayerSchema,
    Source,
    SqliteConnectionConfig,
)


class TestQueryBuilderGroupBy:
    def test_simple_group_by(self):
        """Test simple group by with aggregation functions"""
        schema = SemanticLayerSchema(
            name="test",
            source=Source(
                type="sqlite",
                table="sales",
                connection=SqliteConnectionConfig(file_path=":memory:"),
            ),
            columns=[
                Column(name="category", type="string"),
                Column(name="avg_value", type="float", expression="avg(value)"),
                Column(name="count", type="integer", expression="count(*)"),
            ],
            group_by=["category"],
        )

        builder = QueryBuilder(schema)
        query = builder.build_query()

        expected = (
            "SELECT category, avg(value) as avg_value, count(*) as count "
            "FROM sales GROUP BY category"
        )
        assert query == expected

    def test_group_by_with_case_expression(self):
        """Test group by with CASE expression"""
        schema = SemanticLayerSchema(
            name="test",
            source=Source(
                type="sqlite",
                table="customers",
                connection=SqliteConnectionConfig(file_path=":memory:"),
            ),
            columns=[
                Column(
                    name="age_group",
                    type="string",
                    expression="case when age < 30 then 'Young' when age < 50 then 'Middle' else 'Senior' end",
                ),
                Column(name="avg_spend", type="float", expression="avg(spend)"),
                Column(name="customer_count", type="integer", expression="count(*)"),
            ],
            group_by=["age_group"],
        )

        builder = QueryBuilder(schema)
        query = builder.build_query()

        expected = (
            "SELECT case when age < 30 then 'Young' when age < 50 then 'Middle' else 'Senior' end as age_group, "
            "avg(spend) as avg_spend, count(*) as customer_count "
            "FROM customers "
            "GROUP BY case when age < 30 then 'Young' when age < 50 then 'Middle' else 'Senior' end"
        )
        assert query == expected

    def test_multiple_group_by_columns(self):
        """Test grouping by multiple columns"""
        schema = SemanticLayerSchema(
            name="test",
            source=Source(
                type="sqlite",
                table="orders",
                connection=SqliteConnectionConfig(file_path=":memory:"),
            ),
            columns=[
                Column(name="region", type="string"),
                Column(name="product", type="string"),
                Column(name="total_sales", type="float", expression="sum(amount)"),
                Column(name="order_count", type="integer", expression="count(*)"),
            ],
            group_by=["region", "product"],
        )

        builder = QueryBuilder(schema)
        query = builder.build_query()

        expected = (
            "SELECT region, product, sum(amount) as total_sales, count(*) as order_count "
            "FROM orders GROUP BY region, product"
        )
        assert query == expected

    def test_group_by_with_mixed_expressions(self):
        """Test group by with both regular columns and CASE expressions"""
        schema = SemanticLayerSchema(
            name="test",
            source=Source(
                type="sqlite",
                table="sales",
                connection=SqliteConnectionConfig(file_path=":memory:"),
            ),
            columns=[
                Column(name="region", type="string"),
                Column(
                    name="size_category",
                    type="string",
                    expression="case when amount < 100 then 'Small' else 'Large' end",
                ),
                Column(name="total_amount", type="float", expression="sum(amount)"),
                Column(name="transaction_count", type="integer", expression="count(*)"),
            ],
            group_by=["region", "size_category"],
        )

        builder = QueryBuilder(schema)
        query = builder.build_query()

        expected = (
            "SELECT region, case when amount < 100 then 'Small' else 'Large' end as size_category, "
            "sum(amount) as total_amount, count(*) as transaction_count "
            "FROM sales "
            "GROUP BY region, case when amount < 100 then 'Small' else 'Large' end"
        )
        assert query == expected

    def test_no_group_by(self):
        """Test that no GROUP BY clause is added when not specified"""
        schema = SemanticLayerSchema(
            name="test",
            source=Source(
                type="sqlite",
                table="products",
                connection=SqliteConnectionConfig(file_path=":memory:"),
            ),
            columns=[
                Column(name="name", type="string"),
                Column(name="price", type="float"),
            ],
        )

        builder = QueryBuilder(schema)
        query = builder.build_query()

        expected = "SELECT name, price FROM products"
        assert query == expected

    def test_group_by_with_order_by(self):
        """Test group by with order by clause"""
        schema = SemanticLayerSchema(
            name="test",
            source=Source(
                type="sqlite",
                table="sales",
                connection=SqliteConnectionConfig(file_path=":memory:"),
            ),
            columns=[
                Column(name="category", type="string"),
                Column(name="total_sales", type="float", expression="sum(amount)"),
            ],
            group_by=["category"],
            order_by=["total_sales DESC"],
        )

        builder = QueryBuilder(schema)
        query = builder.build_query()

        expected = (
            "SELECT category, sum(amount) as total_sales "
            "FROM sales GROUP BY category ORDER BY total_sales DESC"
        )
        assert query == expected
