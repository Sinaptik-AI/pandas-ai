import logging
from typing import Union, Optional
from .base import VisualizationLibrary

from ._viz_library_types import (
    NoVizLibraryType,
    MatplotlibVizLibraryType,
    PlotlyVizLibraryType,
    SeabornVizLibraryType,
)
from .. import Logger


viz_lib_map = {
    VisualizationLibrary.MATPLOTLIB.value: MatplotlibVizLibraryType,
    VisualizationLibrary.PLOTLY.value: PlotlyVizLibraryType,
    VisualizationLibrary.SEABORN.value: SeabornVizLibraryType,
}


def viz_lib_type_factory(
    viz_lib_type: str = None, logger: Optional[Logger] = None
) -> Union[
    MatplotlibVizLibraryType,
    PlotlyVizLibraryType,
    SeabornVizLibraryType,
]:
    """
    Factory function to get appropriate instance for viz library type.

    Uses `viz_library_types_map` to determine the viz library type class.

    Args:
        viz_lib_type (Optional[str]): A name of the viz library type.
            Defaults to None, an instance of `DefaultVizLibraryType` will be
            returned.
        logger (Optional[str]): If passed, collects logs about correctness
            of the `viz_library_type` argument and what kind of VizLibraryType
            is created.

    Returns:
        (Union[
                MatplotlibVizLibraryType,
                PlotlyVizLibraryType,
                SeabornVizLibraryType,
                DefaultVizLibraryType
        ]): An instance of the output type.
    """

    if viz_lib_type is not None and viz_lib_type not in viz_lib_map and logger:
        possible_types_msg = ", ".join(f"'{type_}'" for type_ in viz_lib_map)
        logger.log(
            f"Unknown value for the parameter `viz_library_type`: '{viz_lib_type}'."
            f"Possible values are: {possible_types_msg} and None for default "
            f"viz library type (miscellaneous).",
            level=logging.WARNING,
        )

    viz_lib_default = NoVizLibraryType
    viz_lib_type_helper = viz_lib_map.get(viz_lib_type, viz_lib_default)()

    if logger:
        logger.log(
            f"{viz_lib_type_helper.__class__} is going to be used.", level=logging.DEBUG
        )

    return viz_lib_type_helper
