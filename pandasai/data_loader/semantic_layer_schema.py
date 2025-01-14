import json
from typing import Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
    root_validator,
)

from pandasai.constants import (
    LOCAL_SOURCE_TYPES,
    REMOTE_SOURCE_TYPES,
    VALID_COLUMN_TYPES,
    VALID_TRANSFORMATION_TYPES,
)


class Column(BaseModel):
    name: str = Field(..., description="Name of the column.")
    type: str = Field(..., description="Data type of the column.")
    description: str = Field(..., description="Description of the column")

    @field_validator("type")
    @classmethod
    def is_column_type_supported(cls, type: str) -> str:
        if type not in VALID_COLUMN_TYPES:
            raise ValueError(f"Unsupported column type: {type}")
        return type


class Transformation(BaseModel):
    type: str = Field(..., description="Type of transformation to be applied.")
    params: Dict[str, str] = Field(
        ..., description="Parameters for the transformation."
    )

    @field_validator("type")
    @classmethod
    def is_transformation_type_supported(cls, type: str) -> str:
        if type not in VALID_TRANSFORMATION_TYPES:
            raise ValueError(f"Unsupported transformation type: {type}")
        return type


class Source(BaseModel):
    type: str = Field(..., description="Type of the data source.")
    connection: Optional[Dict[str, Union[str, int]]] = Field(
        None, description="Connection object of the data source."
    )
    path: Optional[str] = Field(None, description="Path of the local data source.")
    query: Optional[str] = Field(
        None, description="Query to retrieve data from the data source"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_type_and_fields(cls, values):
        _type = values.get("type")
        path = values.get("path")
        connection = values.get("connection")

        if _type in LOCAL_SOURCE_TYPES:
            if not path:
                raise ValueError(
                    f"For local source type '{_type}', 'path' must be defined."
                )
        elif _type in REMOTE_SOURCE_TYPES:
            if not connection:
                raise ValueError(
                    f"For remote source type '{_type}', 'connection' must be defined."
                )
        else:
            raise ValueError(f"Unsupported source type: {_type}")

        return values


class Destination(BaseModel):
    type: str = Field(..., description="Type of the destination.")
    format: str = Field(..., description="Format of the output file.")
    path: str = Field(..., description="Path to save the output file.")


class SemanticLayerSchema(BaseModel):
    name: str = Field(..., description="Dataset name.")
    description: Optional[str] = Field(
        None, description="Dataset’s contents and purpose description."
    )
    columns: Optional[List[Column]] = Field(
        None, description="Structure and metadata of your dataset’s columns"
    )
    source: Source = Field(..., description="Data source for your dataset.")
    order_by: Optional[List[str]] = Field(
        None, description="Ordering criteria for the dataset."
    )
    limit: Optional[int] = Field(
        None, description="Maximum number of records to retrieve."
    )
    transformations: Optional[List[Transformation]] = Field(
        None, description="List of transformations to apply to the data."
    )
    destination: Optional[Destination] = Field(
        None, description="Destination for saving the dataset."
    )
    update_frequency: Optional[str] = Field(
        None, description="Frequency of dataset updates."
    )


def is_schema_source_same(
    schema1: SemanticLayerSchema, schema2: SemanticLayerSchema
) -> bool:
    source1 = schema1.source
    source2 = schema2.source

    return source1.type == source2.type and json.dumps(
        source1.connection, sort_keys=True
    ) == json.dumps(source2.connection, sort_keys=True)
