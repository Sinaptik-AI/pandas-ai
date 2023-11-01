from enum import Enum


class VisualizationLibrary(str, Enum):
    """
    VisualizationLibrary is an enumeration that represents the available
    data visualization libraries.

    Attributes:
        MATPLOTLIB (str): Represents the Matplotlib library.
        SEABORN (str): Represents the Seaborn library.
        PLOTLY (str): Represents the Plotly library.
    """

    MATPLOTLIB = "matplotlib"
    SEABORN = "seaborn"
    PLOTLY = "plotly"

    DEFAULT = "default"
