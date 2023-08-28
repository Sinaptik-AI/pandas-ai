from chart_generator import ChartGenerator

class MatplotlibChartGenerator(ChartGenerator):
    """
    Matplotlib based Chart Generator
    """
 
    def generate_bar(self, df, x, y, **kwargs):
        if "stacked" in kwargs and kwargs["stacked"] == True:
            return df.plot.bar(**kwargs)   
        else:
            return df.plot.bar(x, y, **kwargs)   
    
    def generate_line(self, df, x, y, **kwargs):
        return df.plot.line(x, y, **kwargs)

    def generate_scatter(self, df, x, y, **kwargs):
        return df.plot.scatter(x, y, **kwargs)