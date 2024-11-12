import matplotlib.pyplot as plt
import matplotlib.figure as figure
import matplotlib.axes as axes
from .base_restricted_module import BaseRestrictedModule


class RestrictedMatplotlib(BaseRestrictedModule):
    def __init__(self):
        self.allowed_attributes = [
            # Figure and Axes creation
            "figure",
            "subplots",
            "subplot",
            # Plotting functions
            "plot",
            "scatter",
            "bar",
            "barh",
            "hist",
            "boxplot",
            "violinplot",
            "pie",
            "errorbar",
            "contour",
            "contourf",
            "imshow",
            "pcolor",
            "pcolormesh",
            # Axis manipulation
            "xlabel",
            "ylabel",
            "title",
            "legend",
            "xlim",
            "ylim",
            "axis",
            "xticks",
            "yticks",
            "grid",
            "axhline",
            "axvline",
            # Colorbar
            "colorbar",
            # Text and annotations
            "text",
            "annotate",
            # Styling
            "style",
            # Save and show
            "show",
            "savefig",
            # Color maps
            "get_cmap",
            # 3D plotting
            "axes3d",
            # Utility functions
            "close",
            "clf",
            "cla",
            # Constants
            "rcParams",
        ]

        for attr in self.allowed_attributes:
            if hasattr(plt, attr):
                setattr(self, attr, self._wrap_function(getattr(plt, attr)))

        # Special handling for figure and axes
        self.Figure = self._wrap_class(figure.Figure)
        self.Axes = self._wrap_class(axes.Axes)

    def __getattr__(self, name):
        if name not in self.allowed_attributes:
            raise AttributeError(f"'{name}' is not allowed in RestrictedMatplotlib")
        return getattr(plt, name)
