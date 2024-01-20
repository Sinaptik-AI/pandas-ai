import logging
from typing import Optional, Union

from .. import Logger
from ._output_types import (
    DataFrameOutputType,
    DefaultOutputType,
    NumberOutputType,
    PlotOutputType,
    StringOutputType,
)

output_types_map = {
    "number": NumberOutputType,
    "dataframe": DataFrameOutputType,
    "plot": PlotOutputType,
    "string": StringOutputType,
}


def output_type_factory(
    output_type: str = None, logger: Optional[Logger] = None
) -> Union[
    NumberOutputType,
    DataFrameOutputType,
    PlotOutputType,
    StringOutputType,
    DefaultOutputType,
]:
    """
    Factory function to get appropriate instance for output type.

    Uses `output_types_map` to determine the output type class.

    Args:
        output_type (Optional[str]): A name of the output type.
            Defaults to None, an instance of `DefaultOutputType` will be
            returned.
        logger (Optional[str]): If passed, collects logs about correctness
            of the `output_type` argument and what kind of OutputType
            is created.

    Returns:
        (Union[
            NumberOutputType,
            DataFrameOutputType,
            PlotOutputType,
            StringOutputType,
            DefaultOutputType
        ]): An instance of the output type.
    """
    if output_type is not None and output_type not in output_types_map and logger:
        possible_types_msg = ", ".join(f"'{type_}'" for type_ in output_types_map)
        logger.log(
            f"Unknown value for the parameter `output_type`: '{output_type}'."
            f"Possible values are: {possible_types_msg} and None for default "
            f"output type (miscellaneous).",
            level=logging.WARNING,
        )

    output_type_helper = output_types_map.get(output_type, DefaultOutputType)()

    if logger:
        logger.log(
            f"{output_type_helper.__class__} is going to be used.", level=logging.DEBUG
        )

    return output_type_helper
