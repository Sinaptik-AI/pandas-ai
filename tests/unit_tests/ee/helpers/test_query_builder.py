import unittest

from pandasai.ee.helpers.query_builder import QueryBuilder
from tests.unit_tests.ee.helpers.schema import MULTI_JOIN_SCHEMA, VIZ_QUERY_SCHEMA


class TestQueryBuilder(unittest.TestCase):
    def test_constructor(self):
        query_builder = QueryBuilder(VIZ_QUERY_SCHEMA)
        assert query_builder.schema == VIZ_QUERY_SCHEMA
        assert query_builder.supported_aggregations == {
            "sum",
            "count",
            "avg",
            "min",
            "max",
        }
        assert query_builder.supported_granularities == {
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
        }
        assert query_builder.supported_date_ranges == {
            "last week",
            "last month",
            "this month",
            "this week",
            "today",
            "this year",
            "last year",
        }

    def test_sql_with_json(self):
        query_builder = QueryBuilder(VIZ_QUERY_SCHEMA)

        json_str = {
            "type": "bar",
            "dimensions": ["Orders.ship_country"],
            "measures": ["Orders.order_count"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Country",
                "yLabel": "Number of Orders",
                "title": "Orders Count by Country",
                "legend": {"display": True, "position": "top"},
            },
            "filters": [],
            "order": [{"id": "Orders.order_count", "direction": "asc"}],
        }
        sql_query = query_builder.generate_sql(json_str)
        assert sql_query in [
            "SELECT COUNT(`orders`.`order_count`) AS order_count, `orders`.`ship_country` AS ship_country FROM `orders` GROUP BY ship_country ORDER BY order_count asc",
            "SELECT `orders`.`ship_country` AS ship_country, COUNT(`orders`.`order_count`) AS order_count FROM `orders` GROUP BY ship_country ORDER BY order_count asc",
        ]

    def test_sql_with_filters_in_json(self):
        query_builder = QueryBuilder(VIZ_QUERY_SCHEMA)

        json_str = {
            "type": "bar",
            "dimensions": ["Orders.ship_country"],
            "measures": ["Orders.total_freight"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Country",
                "yLabel": "Total Freight",
                "title": "Total Freight by Country",
                "legend": {"display": True, "position": "top"},
            },
            "filters": [
                {"member": "Orders.total_freight", "operator": "gt", "values": [0]}
            ],
            "order": [{"id": "Orders.total_freight", "direction": "asc"}],
        }
        sql_query = query_builder.generate_sql(json_str)
        assert sql_query in [
            "SELECT `orders`.`ship_country` AS ship_country, SUM(`orders`.`freight`) AS total_freight FROM `orders` GROUP BY ship_country HAVING SUM(`orders`.`freight`) > 0 ORDER BY total_freight asc",
            "SELECT SUM(`orders`.`freight`) AS total_freight, `orders`.`ship_country` AS ship_country FROM `orders` GROUP BY ship_country HAVING SUM(`orders`.`freight`) > 0 ORDER BY total_freight asc",
        ]

    def test_sql_with_filters_on_dimension(self):
        query_builder = QueryBuilder(VIZ_QUERY_SCHEMA)

        json_str = {
            "type": "bar",
            "dimensions": ["Orders.ship_country"],
            "measures": ["Orders.total_freight"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Country",
                "yLabel": "Total Freight",
                "title": "Total Freight by Country",
                "legend": {"display": True, "position": "top"},
            },
            "filters": [
                {
                    "member": "Orders.ship_country",
                    "operator": "equals",
                    "values": ["abc"],
                }
            ],
            "order": [{"id": "Orders.total_freight", "direction": "asc"}],
        }
        sql_query = query_builder.generate_sql(json_str)
        assert sql_query in [
            "SELECT `orders`.`ship_country` AS ship_country, SUM(`orders`.`freight`) AS total_freight FROM `orders` WHERE `orders`.`ship_country` = 'abc' GROUP BY ship_country ORDER BY total_freight asc",
            "SELECT SUM(`orders`.`freight`) AS total_freight, `orders`.`ship_country` AS ship_country FROM `orders` WHERE `orders`.`ship_country` = 'abc' GROUP BY ship_country ORDER BY total_freight asc",
        ]

    def test_sql_with_filters_without_order(self):
        query_builder = QueryBuilder(VIZ_QUERY_SCHEMA)

        json_str = {
            "type": "bar",
            "dimensions": ["Orders.ship_country"],
            "measures": ["Orders.total_freight"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Country",
                "yLabel": "Total Freight",
                "title": "Total Freight by Country",
                "legend": {"display": True, "position": "top"},
            },
            "filters": [
                {
                    "member": "Orders.ship_country",
                    "operator": "equals",
                    "values": ["abc"],
                }
            ],
        }
        sql_query = query_builder.generate_sql(json_str)
        assert sql_query in [
            "SELECT `orders`.`ship_country` AS ship_country, SUM(`orders`.`freight`) AS total_freight FROM `orders` WHERE `orders`.`ship_country` = 'abc' GROUP BY ship_country",
            "SELECT SUM(`orders`.`freight`) AS total_freight, `orders`.`ship_country` AS ship_country FROM `orders` WHERE `orders`.`ship_country` = 'abc' GROUP BY ship_country",
        ]

    def test_sql_with_filters_with_notset_filter(self):
        query_builder = QueryBuilder(VIZ_QUERY_SCHEMA)

        json_str = {
            "type": "bar",
            "dimensions": ["Orders.ship_country"],
            "measures": ["Orders.total_freight"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Country",
                "yLabel": "Total Freight",
                "title": "Total Freight by Country",
                "legend": {"display": True, "position": "top"},
            },
            "filters": [
                {"member": "Orders.total_freight", "operator": "notSet", "values": []}
            ],
            "order": [{"id": "Orders.total_freight", "direction": "asc"}],
        }
        sql_query = query_builder.generate_sql(json_str)
        assert sql_query in [
            "SELECT SUM(`orders`.`freight`) AS total_freight, `orders`.`ship_country` AS ship_country FROM `orders` GROUP BY ship_country HAVING SUM(`orders`.`freight`) IS NULL ORDER BY total_freight asc",
            "SELECT `orders`.`ship_country` AS ship_country, SUM(`orders`.`freight`) AS total_freight FROM `orders` GROUP BY ship_country HAVING SUM(`orders`.`freight`) IS NULL ORDER BY total_freight asc",
        ]

    def test_sql_with_filters_with_set_filter(self):
        query_builder = QueryBuilder(VIZ_QUERY_SCHEMA)

        json_str = {
            "type": "bar",
            "dimensions": ["Orders.ship_country"],
            "measures": ["Orders.total_freight"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Country",
                "yLabel": "Total Freight",
                "title": "Total Freight by Country",
                "legend": {"display": True, "position": "top"},
            },
            "filters": [
                {
                    "member": "Orders.total_freight",
                    "operator": "set",
                    "values": [],
                }
            ],
            "order": [{"id": "Orders.total_freight", "direction": "asc"}],
        }
        sql_query = query_builder.generate_sql(json_str)
        assert sql_query in [
            "SELECT SUM(`orders`.`freight`) AS total_freight, `orders`.`ship_country` AS ship_country FROM `orders` GROUP BY ship_country HAVING SUM(`orders`.`freight`) IS NOT NULL ORDER BY total_freight asc",
            "SELECT `orders`.`ship_country` AS ship_country, SUM(`orders`.`freight`) AS total_freight FROM `orders` GROUP BY ship_country HAVING SUM(`orders`.`freight`) IS NOT NULL ORDER BY total_freight asc",
        ]

    def test_sql_with_filters_with_join(self):
        query_builder = QueryBuilder(MULTI_JOIN_SCHEMA)

        json_str = {
            "type": "bar",
            "dimensions": ["Engagement.activity_type"],
            "measures": ["Sales.total_revenue"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Activity Type",
                "yLabel": "Total Revenue",
                "title": "Total Revenue Generated from Users who Logged in Before Purchase",
                "legend": {"display": True, "position": "top"},
            },
            "joins": [
                {
                    "name": "Engagement",
                    "join_type": "right",
                    "sql": "${Sales.id} = ${Engagement.id}",
                }
            ],
            "filters": [
                {
                    "member": "Engagement.engagement_date",
                    "operator": "beforeDate",
                    "values": ["${Sales.sales_date}"],
                }
            ],
            "order": [{"id": "Sales.total_revenue", "direction": "asc"}],
        }
        sql_query = query_builder.generate_sql(json_str)

        assert (
            sql_query
            == "SELECT `engagement`.`activity_type` AS activity_type, SUM(`sales`.`revenue`) AS total_revenue FROM `sales` RIGHT JOIN `engagement` ON `engagement`.`id` = `sales`.`id` WHERE `engagement`.`engagement_date` < '${Sales.sales_date}' GROUP BY activity_type ORDER BY total_revenue asc"
        )
