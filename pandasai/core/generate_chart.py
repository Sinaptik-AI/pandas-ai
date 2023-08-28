from chart_generator import ChartGenerator
from matplotlib_chart_generator import MatplotlibChartGenerator
from plotly_chart_generator import PlotlyChartGenerator
from typing import Dict


# Chart generator configmap
chart_generators_map: Dict[str, ChartGenerator] = {
    "matplotlib": MatplotlibChartGenerator(),
    "plotly": PlotlyChartGenerator(),
    "seaborn": None,
}

def generate_chart(data, library, chart_type, **kwargs):
    """
    Generate a data visualization chart based on the provided parameters.

    Args:
        data (pandas.DataFrame): The data to be visualized.
        chart_type (str): The type of chart to be generated (e.g., 'bar', 'line', 'scatter', etc.).
        library (str): The visualization library to be used ('matplotlib', 'seaborn', 'plotly').
        **kwargs: Additional keyword arguments required for configuring the chosen chart type.

    Returns:
        The generated chart object.
    """
    x=y=None
    if "x" in kwargs and "y" in kwargs:
        x=kwargs["x"]
        y=kwargs["y"]
        del kwargs["x"]
        del kwargs["y"]
    else:
        print("x and y base parameters should be supplied for the chart generation")
        return None

    chart_generator: ChartGenerator=chart_generators_map[library]
    
    if chart_type == "bar":
        bar_chart=chart_generator.generate_bar(data, x, y, **kwargs)
        return bar_chart
    elif chart_type == "line":
        line_chart=chart_generator.generate_line(data, x, y, **kwargs)
        return line_chart
    elif chart_type == "scatter":
        scatter_chart=chart_generator.generate_scatter(data, x, y, **kwargs)
        return scatter_chart
    else:
        print(chart_type + "is not supported")

