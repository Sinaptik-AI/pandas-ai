from typing import Optional
import pandas as pd
import pytest

from pandasai.ee.agents.visualization_agent.pipeline.code_generator import CodeGenerator
from pandasai.helpers.logger import Logger
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.schemas.df_config import Config
from tests.unit_tests.ee.helpers.schema import VIZ_QUERY_SCHEMA_STR


class TestVizCodeGenerator:
    @pytest.fixture
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

    @pytest.fixture
    def logger(self):
        return Logger()

    @pytest.fixture
    def config_with_direct_sql(self):
        return Config(
            llm=FakeLLM(output=""),
            enable_cache=False,
            direct_sql=True,
        )

    @pytest.fixture
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, sample_df, config):
        return PipelineContext([sample_df], config)

    def test_generate_matplolib_par_code(
        self, context: PipelineContext, logger: Logger
    ):
        code_gen = CodeGenerator()
        context.add("df_schema", VIZ_QUERY_SCHEMA_STR)
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
        logic_unit = code_gen.execute(json_str, context=context, logger=logger)
        assert isinstance(logic_unit, LogicUnitOutput)
        assert (
            logic_unit.output
            == """
import matplotlib.pyplot as plt
import pandas as pd

sql_query="SELECT `orders`.`ship_country` AS ship_country, COUNT(`orders`.`order_count`) AS order_count FROM `orders` GROUP BY ship_country ORDER BY order_count asc"
data = execute_sql_query(sql_query)

plt.bar(data["ship_country"], data["order_count"], label="order_count")
plt.xlabel('Country')
plt.ylabel('Number of Orders')
plt.title('Orders Count by Country')
plt.legend(loc='best')


plt.savefig("charts.png")

result = {"type": "plot","value": "charts.png"}
"""
        )

    def test_generate_matplolib_pie_chart_code(
        self, context: PipelineContext, logger: Logger
    ):
        code_gen = CodeGenerator()
        context.add("df_schema", VIZ_QUERY_SCHEMA_STR)
        json_str = {
            "type": "pie",
            "dimensions": ["Orders.ship_country"],
            "measures": ["Orders.order_count"],
            "timeDimensions": [],
            "options": {
                "title": "Orders Count by Country",
                "legend": {"display": True, "position": "top"},
            },
            "filters": [],
        }
        logic_unit = code_gen.execute(json_str, context=context, logger=logger)
        assert isinstance(logic_unit, LogicUnitOutput)
        assert (
            logic_unit.output
            == """
import matplotlib.pyplot as plt
import pandas as pd

sql_query="SELECT `orders`.`ship_country` AS ship_country, COUNT(`orders`.`order_count`) AS order_count FROM `orders` GROUP BY ship_country"
data = execute_sql_query(sql_query)

plt.pie(data["order_count"], labels=data["ship_country"], autopct='%1.1f%%')
plt.title('Orders Count by Country')
plt.legend(loc='best')


plt.savefig("charts.png")

result = {"type": "plot","value": "charts.png"}
"""
        )

    def test_generate_matplolib_line_chart_code(
        self, context: PipelineContext, logger: Logger
    ):
        code_gen = CodeGenerator()
        context.add("df_schema", VIZ_QUERY_SCHEMA_STR)
        json_str = {
            "type": "line",
            "dimensions": ["Orders.order_date"],
            "measures": ["Orders.order_count"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Order Date",
                "yLabel": "Number of Orders",
                "title": "Orders Over Time",
                "legend": {"display": True, "position": "top"},
            },
            "filters": [],
            "order": [],
        }

        logic_unit = code_gen.execute(json_str, context=context, logger=logger)
        assert isinstance(logic_unit, LogicUnitOutput)
        assert (
            logic_unit.output
            == """
import matplotlib.pyplot as plt
import pandas as pd

sql_query="SELECT `orders`.`order_date` AS order_date, COUNT(`orders`.`order_count`) AS order_count FROM `orders` GROUP BY order_date"
data = execute_sql_query(sql_query)

plt.plot(data["order_date"], data["order_count"])
plt.xlabel('Order Date')
plt.ylabel('Number of Orders')
plt.title('Orders Over Time')
plt.legend(loc='best')


plt.savefig("charts.png")

result = {"type": "plot","value": "charts.png"}
"""
        )

    def test_generate_matplolib_scatter_chart_code(
        self, context: PipelineContext, logger: Logger
    ):
        code_gen = CodeGenerator()
        context.add("df_schema", VIZ_QUERY_SCHEMA_STR)
        json_str = {
            "type": "scatter",
            "dimensions": ["Orders.order_date", "Orders.ship_via"],
            "measures": [],
            "timeDimensions": [],
            "options": {"title": "Total Freight by Order Date"},
            "filters": [],
            "order": [],
        }

        logic_unit = code_gen.execute(json_str, context=context, logger=logger)
        assert isinstance(logic_unit, LogicUnitOutput)
        assert (
            logic_unit.output
            == """
import matplotlib.pyplot as plt
import pandas as pd

sql_query="SELECT `orders`.`order_date` AS order_date, `orders`.`ship_via` AS ship_via FROM `orders` GROUP BY order_date, ship_via"
data = execute_sql_query(sql_query)

plt.scatter(data['order_date'], data['ship_via'])
plt.title('Total Freight by Order Date')
plt.legend(loc='best')


plt.savefig("charts.png")

result = {"type": "plot","value": "charts.png"}
"""
        )

    def test_generate_matplolib_histogram_chart_code(
        self, context: PipelineContext, logger: Logger
    ):
        code_gen = CodeGenerator()
        context.add("df_schema", VIZ_QUERY_SCHEMA_STR)
        json_str = {
            "type": "histogram",
            "dimensions": [],
            "measures": ["Orders.total_freight"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Total Freight",
                "yLabel": "Frequency",
                "title": "Distribution of Total Freight",
                "legend": {"display": False},
                "bins": 30,
            },
            "filters": [],
        }

        logic_unit = code_gen.execute(json_str, context=context, logger=logger)
        assert isinstance(logic_unit, LogicUnitOutput)
        assert (
            logic_unit.output
            == """
import matplotlib.pyplot as plt
import pandas as pd

sql_query="SELECT SUM(`orders`.`freight`) AS total_freight FROM `orders`"
data = execute_sql_query(sql_query)

plt.hist(data['total_freight'])
plt.xlabel('Total Freight')
plt.ylabel('Frequency')
plt.title('Distribution of Total Freight')


plt.savefig("charts.png")

result = {"type": "plot","value": "charts.png"}
"""
        )

    def test_generate_matplolib_boxplot_chart_code(
        self, context: PipelineContext, logger: Logger
    ):
        code_gen = CodeGenerator()
        context.add("df_schema", VIZ_QUERY_SCHEMA_STR)
        json_str = {
            "type": "boxplot",
            "dimensions": ["Orders.ship_country"],
            "measures": ["Orders.total_freight"],
            "timeDimensions": [],
            "options": {
                "xLabel": "Shipping Country",
                "yLabel": "Total Freight",
                "title": "Distribution of Total Freight by Shipping Country",
                "legend": {"display": False},
            },
            "filters": [],
            "order": [],
        }

        logic_unit = code_gen.execute(json_str, context=context, logger=logger)
        assert isinstance(logic_unit, LogicUnitOutput)
        assert (
            logic_unit.output
            == """
import matplotlib.pyplot as plt
import pandas as pd

sql_query="SELECT `orders`.`ship_country` AS ship_country, SUM(`orders`.`freight`) AS total_freight FROM `orders` GROUP BY ship_country"
data = execute_sql_query(sql_query)

plt.boxplot(data['total_freight'])
plt.xlabel('Shipping Country')
plt.ylabel('Total Freight')
plt.title('Distribution of Total Freight by Shipping Country')


plt.savefig("charts.png")

result = {"type": "plot","value": "charts.png"}
"""
        )
