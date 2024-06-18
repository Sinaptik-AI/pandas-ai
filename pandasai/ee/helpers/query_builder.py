import re

from pandasai.exceptions import InvalidSchemaJson

MISSING_TABLE_NAME_MESSAGE = "All measures, dimensions, timeDimensions, order and filters must have the format Table_Name.Dimension or Table_Name.Measure"
TABLE_NOT_FOUND_MESSAGE = "Table {0} Doesn't exist"


class QueryBuilder:
    """
    Creates query from json structure
    """

    def __init__(self, schema):
        self.schema = schema
        self.supported_aggregations = {"sum", "count", "avg", "min", "max"}
        self.supported_granularities = {
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
        }
        self.supported_date_ranges = {
            "last week",
            "last month",
            "this month",
            "this week",
            "today",
            "this year",
            "last year",
        }

    def generate_sql(self, query):
        self._validate_query(query)
        measures = query.get("measures", [])
        dimensions = query.get("dimensions", [])
        time_dimensions = query.get("timeDimensions", [])
        filters = query.get("filters", [])

        columns = self._generate_columns(dimensions, time_dimensions, measures)

        referenced_tables = self._get_referenced_tables(
            dimensions, time_dimensions, measures, filters
        )
        main_table_entry = self._get_main_table_entry(measures, dimensions)

        if not main_table_entry:
            raise ValueError("Table not found in schema.")

        sql = self._build_select_clause(columns)
        sql += self._build_from_clause(main_table_entry)
        sql += self._build_joins_clause(main_table_entry, referenced_tables)
        sql += self._build_where_clause(filters, time_dimensions)
        sql += self._build_group_by_clause(dimensions, time_dimensions)
        sql += self._build_having_clause(filters)
        sql += self._build_order_clause(query)
        sql += self._build_limit_clause(query)

        return sql

    def _validate_table(self, value: str):
        value_splitted = value.split(".")
        if len(value_splitted) == 1:
            raise InvalidSchemaJson(MISSING_TABLE_NAME_MESSAGE)

        table = self.find_table(value_splitted[0])
        if not table:
            raise InvalidSchemaJson(TABLE_NOT_FOUND_MESSAGE.format(value_splitted[0]))

    def _validate_query(self, query: dict):
        for measure in query.get("measures", []):
            self._validate_table(measure)

        for dimension in query.get("dimensions", []):
            self._validate_table(dimension)

        for dimension in query.get("timeDimensions", []):
            self._validate_table(dimension["dimension"])

        for order in query.get("order", []):
            self._validate_table(order["id"])

        for filter in query.get("filters", []):
            self._validate_table(filter["member"])

    def _validate_fix_query(self, query):
        for index, measure in enumerate(query.get("measures", [])):
            query["measures"][index] = self._validate_and_fix_mapped_measure(measure)

        for index, dimension in enumerate(query.get("dimensions", [])):
            query["dimensions"][index] = self._validate_and_fix_mapped_dimension(
                dimension
            )

        for index, dimension in enumerate(query.get("timeDimensions", [])):
            query["timeDimensions"][index][
                "dimension"
            ] = self._validate_and_fix_mapped_dimension(dimension["dimension"])

        for index, order in enumerate(query.get("order", [])):
            query["order"][index]["id"] = self._validate_and_fix_mapped_order(
                order["id"]
            )

        for index, filter in enumerate(query.get("filters", [])):
            query["filters"][index]["member"] = self._validate_and_fix_mapped_order(
                filter["member"]
            )

        return query

    def _generate_columns(self, dimensions, time_dimensions, measures):
        all_dimensions = list(dict.fromkeys(dimensions))
        # + [td["dimension"] for td in time_dimensions]
        columns = []

        for dim in all_dimensions:
            table = self.find_table(dim.split(".")[0])["table"]
            dimension_info = self.find_dimension(dim)
            sql_expr = dimension_info.get("sql")
            name = dimension_info["name"]
            if sql_expr:
                columns.append(f"`{table}`.`{sql_expr}` AS {name}")
            else:
                columns.append(f"{name}")

        for measure in measures:
            table = self.find_table(measure.split(".")[0])["table"]
            measure_info = self.find_measure(measure)
            if measure_info["type"] not in self.supported_aggregations:
                raise ValueError(
                    f"Unsupported aggregation type '{measure_info['type']}' for measure '{measure_info['name']}'. Supported types are: {', '.join(self.supported_aggregations)}"
                )
            sql_expr = measure_info.get("sql") or measure_info["name"]
            columns.append(
                f"{measure_info['type'].upper()}(`{table}`.`{sql_expr}`) AS {measure_info['name']}"
            )

        for time_dimension in time_dimensions:
            columns.append(self._generate_time_dimension_column(time_dimension))

        return list(dict.fromkeys(columns))  # preserve order and return unique columns

    def _validate_and_fix_mapped_measure(self, value):
        value_splitted = value.split(".")
        if len(value_splitted) == 1:
            table_name = self._find_table_name_in_measure_if_not_exists(
                value_splitted[0]
            )
            if table_name is None:
                raise ValueError(
                    "Measure must have table expected format is TableName.measure"
                )
            return f"{table_name}.{value_splitted[0]}"
        return value

    def _validate_and_fix_mapped_dimension(self, value):
        value_splitted = value.split(".")
        if len(value_splitted) == 1:
            table_name = self._find_table_name_in_dimension_if_not_exists(
                value_splitted[0]
            )
            if table_name is None:
                raise ValueError(
                    "Measure must have table expected format is TableName.measure"
                )
            return f"{table_name}.{value_splitted[0]}"
        return value

    def _validate_and_fix_mapped_order(self, value):
        value_splitted = value.split(".")
        if len(value_splitted) == 1:
            table_name = self._find_table_name_in_orders_if_not_exists(
                value_splitted[0]
            )
            if table_name is None:
                raise ValueError(
                    "Measure must have table expected format is TableName.measure"
                )
            return f"{table_name}.{value_splitted[0]}"
        return value

    def _validate_and_fix_mapped_filter(self, value):
        value_splitted = value.split(".")
        if len(value_splitted) == 1:
            table_name = self._find_table_name_in_filter_if_not_exists(
                value_splitted[0]
            )
            if table_name is None:
                raise ValueError(
                    "Measure must have table expected format is TableName.measure"
                )
            return f"{table_name}.{value_splitted[0]}"
        return value

    def _find_table_name_in_filter_if_not_exists(self, filter_name: str):
        """
        Find and add table name if not exists in Measure
        """
        for table in self.schema:
            for dimension in table["dimensions"]:
                if dimension["name"] == filter_name:
                    return table["name"]

        return None

    def _find_table_name_in_measure_if_not_exists(self, measure_name: str):
        """
        Find and add table name if not exists in Measure
        """
        for table in self.schema:
            for measure in table["measures"]:
                if measure["name"] == measure_name:
                    return table["name"]

        return None

    def _find_table_name_in_dimension_if_not_exists(self, dimension_name: str):
        """
        Find and add table name if not exists in Measure
        """
        for table in self.schema:
            for dimension in table["dimensions"]:
                if dimension["name"] == dimension_name:
                    return table["name"]

        return None

    def _find_table_name_in_orders_if_not_exists(self, dimension_name: str):
        """
        Find and add table name if not exists in Measure
        """
        for table in self.schema:
            for dimension in table["dimensions"]:
                if dimension["name"] == dimension_name:
                    return table["name"]

            for measure in table["measures"]:
                if measure["name"] == dimension_name:
                    return table["name"]

        return None

    def _generate_time_dimension_column(self, time_dimension):
        dimension = time_dimension["dimension"]
        granularity = (
            time_dimension["granularity"] if "granularity" in time_dimension else "day"
        )

        if granularity not in self.supported_granularities:
            raise ValueError(
                f"Unsupported granularity '{granularity}'. Supported granularities are: {', '.join(self.supported_granularities)}"
            )

        table = self.find_table(dimension.split(".")[0])["table"]
        dimension_info = self.find_dimension(dimension)
        sql_expr = f"`{table}`.`{dimension_info['sql']}`"

        granularity_sql = {
            "year": f"YEAR({sql_expr})",
            "month": f"DATE_FORMAT({sql_expr}, '%Y-%m')",
            "day": f"DATE_FORMAT({sql_expr}, '%Y-%m-%d')",
            "hour": f"HOUR({sql_expr})",
            "minute": f"MINUTE({sql_expr})",
            "second": f"SECOND({sql_expr})",
        }

        if granularity not in granularity_sql:
            raise ValueError(f"Unhandled granularity: {granularity}")

        return f"{granularity_sql[granularity]} AS {dimension_info['name']}_by_{granularity}"

    def _get_referenced_tables(self, dimensions, time_dimensions, measures, filters):
        return (
            {measure.split(".")[0] for measure in measures}
            | {dim.split(".")[0] for dim in dimensions}
            | {td["dimension"].split(".")[0] for td in time_dimensions}
            | {filter["member"].split(".")[0] for filter in filters}
        )

    def _get_main_table_entry(self, measures, dimensions):
        main_table = (
            measures[0].split(".")[0] if measures else dimensions[0].split(".")[0]
        )
        return next(
            (table for table in self.schema if table["name"] == main_table), None
        )

    def _build_select_clause(self, columns):
        return "SELECT " + ", ".join(columns)

    def _build_from_clause(self, main_table_entry):
        return f" FROM `{main_table_entry['table']}`"

    def _build_joins_clause(self, main_table_entry, referenced_tables):
        sql = ""
        main_table = main_table_entry["name"]

        for table_name in referenced_tables:
            if table_name != main_table:
                table_entry = next(
                    (table for table in self.schema if table["name"] == table_name),
                    None,
                )
                if not table_entry:
                    raise ValueError(f"Table '{table_name}' not found in schema.")
                if "joins" in table_entry and (
                    join := next(
                        (
                            j
                            for j in table_entry["joins"]
                            if j["name"] in {main_table, table_name}
                        ),
                        None,
                    )
                ):
                    join_condition = self.resolve_template_literals(join["sql"])
                    sql += f" {join['join_type'].upper()} JOIN `{table_entry['table']}` ON {join_condition}"

        return sql

    def _build_where_clause(self, filters, time_dimensions):
        filter_statements = [
            self.process_filter(filter)
            for filter in filters
            if self.find_dimension(filter["member"]).get("name") is not None
        ]
        time_dimension_filters = [
            self.resolve_date_range(td) for td in time_dimensions if "dateRange" in td
        ]
        filter_statements.extend(time_dimension_filters)

        return f" WHERE {' AND '.join(filter_statements)}" if filter_statements else ""

    def _build_group_by_clause(self, dimensions, time_dimensions):
        if not (time_dimensions or dimensions):
            return ""

        group_by_dimensions = [
            self.find_dimension(dim)["name"] for dim in dimensions
        ] + [
            f"{self.find_dimension(td['dimension'])['name']}_by_{td.get('granularity', 'day')}"
            for td in time_dimensions
        ]

        return " GROUP BY " + ", ".join(group_by_dimensions)

    def _build_having_clause(self, filters):
        filter_statements = [
            self.process_filter(filter)
            for filter in filters
            if self.find_measure(filter["member"]).get("name") is not None
        ]

        return f" HAVING {' AND '.join(filter_statements)}" if filter_statements else ""

    def _build_order_clause(self, query):
        if "order" not in query or len(query["order"]) == 0:
            return ""

        order_clauses = []
        for order in query["order"]:
            name = None
            if measure := self.find_measure(order["id"]):
                name = measure["name"]

            if (
                name is None
                and "timeDimensions" in query
                and len(query["timeDimensions"]) > 0
            ):
                for time_dimension in query["timeDimensions"]:
                    if (
                        dimension
                        := f"{self.find_dimension(order['id'])['name']}_by_{time_dimension['granularity']}"
                    ):
                        name = dimension

            if name is None and "dimensions" in query and len(query["dimensions"]) > 0:
                if dimension := self.find_dimension(order["id"]):
                    name = dimension["name"]

            if name is None:
                name = (
                    self.find_measure(order["id"]) or self.find_dimension(order["id"])
                )["name"]

            order_clauses.append(f"{name} {order['direction']}")

        return f" ORDER BY {', '.join(order_clauses)}"

    def _build_limit_clause(self, query):
        return f" LIMIT {query['limit']}" if "limit" in query else ""

    def resolve_date_range(self, time_dimension):
        dimension = time_dimension["dimension"]
        date_range = time_dimension["dateRange"]
        table_name = dimension.split(".")[0]
        dimension_info = self.find_dimension(dimension)
        table = self.find_table(table_name)

        if not table or not dimension_info:
            raise ValueError(f"Dimension '{dimension}' not found in schema.")

        table_column = f"`{table['table']}`.`{dimension_info['sql']}`"

        if isinstance(date_range, list) and len(date_range) == 2:
            start_date, end_date = date_range
            return f"{table_column} BETWEEN '{start_date}' AND '{end_date}'"
        else:
            if isinstance(date_range, list) and len(date_range) == 1:
                date_range = date_range[0]

            if date_range not in self.supported_date_ranges:
                raise ValueError(f"Unsupported date range: {date_range}")

            if date_range == "last week":
                return f"{table_column} >= CURRENT_DATE - INTERVAL '1 week' AND {table_column} < CURRENT_DATE"
            elif date_range == "last month":
                return f"{table_column} >= CURRENT_DATE - INTERVAL '1 month' AND {table_column} < CURRENT_DATE"
            elif date_range == "this month":
                return f"{table_column} >= DATE_TRUNC('month', CURRENT_DATE) AND {table_column} < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'"
            elif date_range == "this week":
                return f"{table_column} >= DATE_TRUNC('week', CURRENT_DATE) AND {table_column} < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'"
            elif date_range == "today":
                return f"{table_column} >= DATE_TRUNC('day', CURRENT_DATE) AND {table_column} < DATE_TRUNC('day', CURRENT_DATE) + INTERVAL '1 day'"
            elif date_range == "this year":
                return f"{table_column} >= DATE_TRUNC('year', CURRENT_DATE) AND {table_column} < DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '1 year'"
            elif date_range == "last year":
                return f"{table_column} >= DATE_TRUNC('year', CURRENT_DATE - INTERVAL '1 year') AND {table_column} < DATE_TRUNC('year', CURRENT_DATE)"

    def process_filter(self, filter):
        required_keys = ["member", "operator", "values"]

        # Check if any required key is missing or if "values" is empty
        if any(key not in filter for key in required_keys) or (
            not filter.get("values")
            and filter.get("operator", None) not in ["set", "notSet"]
        ):
            raise ValueError(f"Invalid filter: {filter}")

        table_name = filter["member"].split(".")[0]
        dimension = self.find_dimension(filter["member"])
        measure = self.find_measure(filter["member"])

        if dimension:
            table_column = f"`{self.find_table(table_name)['table']}`.`{dimension.get('sql', dimension['name'])}`"
        elif measure:
            table_column = f"{measure['type'].upper()}(`{self.find_table(table_name)['table']}`.`{measure.get('sql', measure['name'])}`)"
        else:
            raise ValueError(f"Member '{filter['member']}' not found in schema.")

        operator = filter["operator"]
        values = filter["values"]

        single_value_operators = {
            "equals": "=",
            "notEquals": "!=",
            "contains": "LIKE",
            "notContains": "NOT LIKE",
            "startsWith": "LIKE",
            "endsWith": "LIKE",
            "gt": ">",
            "gte": ">=",
            "lt": "<",
            "lte": "<=",
            "beforeDate": "<",
            "afterDate": ">",
            "in": "IN",
        }

        multi_value_operators = {"equals": "IN", "notEquals": "NOT IN"}

        return self._build_query_condition(
            operator,
            table_column,
            values,
            single_value_operators,
            multi_value_operators,
        )

    def _build_query_condition(
        self,
        operator,
        table_column,
        values,
        single_value_operators,
        multi_value_operators,
    ):
        if operator in single_value_operators:
            if operator in ["equals", "notEquals", "in"]:
                if len(values) == 1:
                    operator_str = "=" if operator == "equals" else "!="
                    return f"{table_column} {operator_str} '{values[0]}'"
                else:
                    operator_str = "IN" if operator in ["equals", "in"] else "NOT IN"
                    formatted_values = "', '".join(values)
                    return f"{table_column} {operator_str} ('{formatted_values}')"

            elif operator in ["contains", "notContains", "startsWith", "endsWith"]:
                pattern = {
                    "contains": f"%{values[0]}%",
                    "notContains": f"%{values[0]}%",
                    "startsWith": f"{values[0]}%",
                    "endsWith": f"%{values[0]}",
                }[operator]
                return f"{table_column} {single_value_operators[operator]} '{pattern}'"

            else:
                value = f"'{values[0]}'" if isinstance(values[0], str) else values[0]
                return f"{table_column} {single_value_operators[operator]} {value}"

        elif operator in multi_value_operators:
            formatted_values = "', '".join(values)
            return f"{table_column} {multi_value_operators[operator]} ('{formatted_values}')"

        elif operator == "set":
            return f"{table_column} IS NOT NULL"

        elif operator == "notSet":
            return f"{table_column} IS NULL"

        elif operator in ["inDateRange", "notInDateRange"]:
            if len(values) != 2:
                raise ValueError(f"Invalid number of values for '{operator}' operator.")
            range_operator = "BETWEEN" if operator == "inDateRange" else "NOT BETWEEN"
            return f"{table_column} {range_operator} '{values[0]}' AND '{values[1]}'"

        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def resolve_template_literals(self, template):
        def replace_column(match):
            table, column = match.group(1).split(".")
            new_table = self.find_table(table)
            if not new_table:
                raise ValueError(f"Table '{table}' not found in schema.")
            new_column = next(
                (dim for dim in new_table["dimensions"] if dim["name"] == column), None
            )
            if not new_column:
                raise ValueError(f"Column '{column}' not found in schema.")
            return f"`{new_table['table']}`.`{new_column['sql']}`"

        return re.sub(r"\$\{([^}]+)\}", replace_column, template)

    def find_table(self, table_name):
        return next((table for table in self.schema if table["name"] == table_name), {})

    def find_dimension(self, dimension):
        table_name, dim_name = dimension.split(".")
        table = self.find_table(table_name)
        dim = next(
            (dim for dim in table.get("dimensions", []) if dim.get("name") == dim_name),
            {},
        )
        return dim

    def find_measure(self, measure):
        table_name, measure_name = measure.split(".")
        table = self.find_table(table_name)
        meas = next(
            (
                meas
                for meas in table.get("measures", [])
                if meas.get("name") == measure_name
            ),
            {},
        )
        return meas
