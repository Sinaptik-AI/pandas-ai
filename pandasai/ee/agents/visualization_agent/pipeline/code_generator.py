import json
from typing import Any, Callable

from pandasai.ee.helpers.query_builder import QueryBuilder
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.pipeline_context import PipelineContext


class CodeGenerator(BaseLogicUnit):
    """
    LLM Code Generation Stage
    """

    def __init__(
        self, on_code_generation: Callable[[str, Exception], None] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.on_code_generation = on_code_generation

    def execute(self, input: Any, **kwargs) -> Any:
        """
        This method will return output according to
        Implementation.

        :param input: Your input data.
        :param kwargs: A dictionary of keyword arguments.
            - 'logger' (any): The logger for logging.
            - 'config' (Config): Global configurations for the test
            - 'context' (any): The execution context.

        :return: The result of the execution.
        """
        pipeline_context: PipelineContext = kwargs.get("context")
        logger: Logger = kwargs.get("logger")
        schema = json.loads(pipeline_context.get("df_schema"))
        query_builder = QueryBuilder(schema)

        sql_query = query_builder.generate_sql(input)

        matplotlib_code = self.generate_matplotlib_code(input)

        code = f"""
import matplotlib.pyplot as plt
import pandas as pd

sql_query="{sql_query}"
data = execute_sql_query(sql_query)

{matplotlib_code}

plt.savefig("charts.png")

result = {{"type": "plot","value": "charts.png"}}
"""

        logger.log(f"""Code Generated: {code}""")

        # Implement error handling pipeline here...

        return LogicUnitOutput(
            code,
            True,
            "Code Generated Successfully",
            {"content_type": "string", "value": code},
        )

    def generate_matplotlib_code(self, query):
        chart_type = query["type"]
        x_label = query["options"].get("xLabel", None)
        y_label = query["options"].get("yLabel", None)
        title = query["options"].get("title", None)
        legend_display = query["options"]["legend"].get("display", None)
        legend_position = query["options"]["legend"].get("position", None)
        legend_position = (
            legend_position
            in [
                "best",
                "upper right",
                "upper left",
                "lower left",
                "lower right",
                "right",
                "center left",
                "center right",
                "lower center",
                "upper center",
                "center",
            ]
            or "best"
        )

        code = ""

        if chart_type == "bar":
            code += self._generate_bar_code(query)
        elif chart_type == "line":
            code += self._generate_line_code(query)
        elif chart_type == "scatter":
            code += self._generate_scatter_code(query)
        elif chart_type == "hist":
            code += self._generate_hist_code(query)
        elif chart_type == "box":
            code += self._generate_box_code(query)

        code += (
            f"plt.xlabel('{x_label}')\n"
            f"plt.ylabel('{y_label}')\n"
            f"plt.title('{title}')\n"
        )

        if legend_display:
            code += f"plt.legend(loc='{legend_position}')\n"

        return code

    def _generate_bar_code(self, query):
        x_key = query["dimensions"][0].split(".")[1]
        plots = ""
        for measure in query["measures"]:
            if isinstance(measure, str):
                field_name = measure.split(".")[1]
                label = field_name
            else:
                field_name = measure["id"].split(".")[1]
                label = measure["label"]

            plots += (
                f"""plt.bar(data["{x_key}"], data["{field_name}"], label="{label}")\n"""
            )

        return plots

    def _generate_line_code(self, query):
        x_key = query["dimensions"][0].split(".")[1]
        plots = ""
        for measure in query["measures"]:
            field_name = measure.split(".")[1]
            plots += f"""plt.plot(data["{x_key}"], data["{field_name}"])\n"""

        return plots

    def _generate_scatter_code(self, query):
        x_key = query["dimensions"][0].split(".")[1]
        y_key = query["measures"][0].split(".")[1]
        return f"plt.scatter(data['{x_key}'], data['{y_key}'])\n"

    def _generate_hist_code(self, query):
        y_key = query["measures"][0].split(".")[1]
        return f"plt.hist(data['{y_key}'])\n"

    def _generate_box_code(self, query):
        y_key = query["measures"][0].split(".")[1]
        return f"plt.boxplot(data['{y_key}'])\n"
