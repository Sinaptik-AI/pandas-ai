from typing import Union

from ._output_types import (
    NumberOutputType,
    DataFrameOutputType,
    PlotOutputType,
    StringOutputType,
    DefaultOutputType,
)

output_types_map = {
    "number": NumberOutputType,
    "dataframe": DataFrameOutputType,
    "plot": PlotOutputType,
    "string": StringOutputType,
}


def output_type_factory(
    output_type,
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
        output_type (str): A name of the output type.

    Returns:
        (Union[
            NumberOutputType,
            DataFrameOutputType,
            PlotOutputType,
            StringOutputType,
            DefaultOutputType
        ]): An instance of the output type.
    """
    return output_types_map.get(output_type, DefaultOutputType)()
