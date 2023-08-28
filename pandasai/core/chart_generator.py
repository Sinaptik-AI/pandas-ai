from abc import ABC, abstractmethod

class ChartGenerator(ABC):
    """
    Abstract class "ChartGenerator" comprises the set of abstract generate_<chart> methods to be 
    implemented in the child/sub classes for chart generation library packages
    """
 
    @abstractmethod
    def generate_bar(self, dataframe, x, y, **kwargs):
        pass

    @abstractmethod
    def generate_line(self, dataframe, x, y, **kwargs):
        pass

    @abstractmethod
    def generate_scatter(self, dataframe, x, y, **kwargs):
        pass