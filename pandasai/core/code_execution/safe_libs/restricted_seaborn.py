import seaborn as sns

from .base_restricted_module import BaseRestrictedModule


class RestrictedSeaborn(BaseRestrictedModule):
    def __init__(self):
        self.allowed_attributes = [
            # Plot functions
            "scatterplot",
            "lineplot",
            "relplot",
            "displot",
            "histplot",
            "kdeplot",
            "ecdfplot",
            "rugplot",
            "distplot",
            "boxplot",
            "violinplot",
            "boxenplot",
            "stripplot",
            "swarmplot",
            "barplot",
            "countplot",
            "heatmap",
            "clustermap",
            "regplot",
            "lmplot",
            "residplot",
            "jointplot",
            "pairplot",
            "catplot",
            # Axis styling
            "set_style",
            "set_context",
            "set_palette",
            "despine",
            "move_legend",
            "axes_style",
            "plotting_context",
            # Color palette functions
            "color_palette",
            "palplot",
            "cubehelix_palette",
            "light_palette",
            "dark_palette",
            "diverging_palette",
            # Utility functions
            "load_dataset",
            # Figure-level interface
            "FacetGrid",
            "PairGrid",
            "JointGrid",
            # Regression and statistical estimation
            "lmplot",
            "regplot",
            "residplot",
            # Matrix plots
            "heatmap",
            "clustermap",
            # Miscellaneous
            "kdeplot",
            "rugplot",
        ]

        for attr in self.allowed_attributes:
            if hasattr(sns, attr):
                setattr(self, attr, self._wrap_function(getattr(sns, attr)))

    def __getattr__(self, name):
        if name not in self.allowed_attributes:
            raise AttributeError(f"'{name}' is not allowed in RestrictedSeaborn")
        return getattr(sns, name)
