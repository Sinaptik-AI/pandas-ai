from chart_generator import ChartGenerator
import plotly.express as px

class PlotlyChartGenerator(ChartGenerator):
    """
    Plotly based Chart Generator
    """
 
    def generate_bar(self, df, x, y, **kwargs):
        return px.bar(df, x, y, **kwargs)   
    
    def generate_line(self, df, x, y, **kwargs):
        return px.line(df, x, y, **kwargs)

    def generate_scatter(self, df, x, y, **kwargs):
        return px.scatter(df, x, y, **kwargs)