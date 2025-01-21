import json
import re
from functools import partial
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from pandasai.constants import (
    LOCAL_SOURCE_TYPES,
    REMOTE_SOURCE_TYPES,
    VALID_COLUMN_TYPES,
    VALID_TRANSFORMATION_TYPES,
)


class Column(BaseModel):
    name: str = Field(..., description="Name of the column.")
    type: Optional[str] = Field(None, description="Data type of the column.")
    description: Optional[str] = Field(None, description="Description of the column")

    @field_validator("type")
    @classmethod
    def is_column_type_supported(cls, type: str) -> str:
        if type not in VALID_COLUMN_TYPES:
            raise ValueError(
                f"Unsupported column type: {type}. Supported types are: {VALID_COLUMN_TYPES}"
            )
        return type


class Relation(BaseModel):
    name: Optional[str] = Field(None, description="Name of the relationship.")
    description: Optional[str] = Field(
        None, description="Description of the relationship."
    )
    from_: str = Field(
        ..., alias="from", description="Source column for the relationship."
    )
    to: str = Field(..., description="Target column for the relationship.")


class Transformation(BaseModel):
    type: str = Field(..., description="Type of transformation to be applied.")
    params: Optional[Dict[str, str]] = Field(
        None, description="Parameters for the transformation."
    )

    @field_validator("type")
    @classmethod
    def is_transformation_type_supported(cls, type: str) -> str:
        if type not in VALID_TRANSFORMATION_TYPES:
            raise ValueError(f"Unsupported transformation type: {type}")
        return type


class Source(BaseModel):
    type: str = Field(..., description="Type of the data source.")
    path: Optional[str] = Field(None, description="Path of the local data source.")
    connection: Optional[Dict[str, Union[str, int]]] = Field(
        None, description="Connection object of the data source."
    )
    table: Optional[str] = Field(None, description="Table of the data source.")
    view: Optional[bool] = Field(False, description="Whether table is a view")

    @model_validator(mode="before")
    @classmethod
    def validate_type_and_fields(cls, values):
        _type = values.get("type")
        path = values.get("path")
        table = values.get("table")
        view = values.get("view")
        connection = values.get("connection")

        if _type in LOCAL_SOURCE_TYPES:
            if not path:
                raise ValueError(
                    f"For local source type '{_type}', 'path' must be defined."
                )
            if view:
                raise ValueError("A view cannot be used with a local source type.")
        elif _type in REMOTE_SOURCE_TYPES:
            if not connection:
                raise ValueError(
                    f"For remote source type '{_type}', 'connection' must be defined."
                )
            if table and view:
                raise ValueError("Only one of 'table' or 'view' can be defined.")
            if not table and not view:
                raise ValueError("Either 'table' or 'view' must be defined.")
        else:
            raise ValueError(f"Unsupported source type: {_type}")

        return values


class Destination(BaseModel):
    type: str = Field(..., description="Type of the destination.")
    format: str = Field(..., description="Format of the output file.")
    path: str = Field(..., description="Path to save the output file.")

    @field_validator("format")
    @classmethod
    def is_format_supported(cls, format: str) -> str:
        if format not in LOCAL_SOURCE_TYPES:
            raise ValueError(f"Unsupported destination format: {format}")
        return format


class SemanticLayerSchema(BaseModel):
    name: str = Field(..., description="Dataset name.")
    source: Source = Field(..., description="Data source for your dataset.")
    description: Optional[str] = Field(
        None, description="Dataset’s contents and purpose description."
    )
    columns: Optional[List[Column]] = Field(
        None, description="Structure and metadata of your dataset’s columns"
    )
    relations: Optional[List[Relation]] = Field(
        None, description="Relationships between columns and tables."
    )
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

    @model_validator(mode="after")
    def check_columns_relations(self):
        column_re_check = r"^[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$"
        is_view_column_name = partial(re.match, column_re_check)

        # unpack columns info
        _columns = self.columns
        _column_names = [col.name for col in _columns or ()]
        _tables_names_in_columns = {
            column_name.split(".")[0] for column_name in _column_names or ()
        }

        if len(_column_names) != len(set(_column_names)):
            raise ValueError("Column names must be unique. Duplicate names found.")

        if self.source.view:
            # unpack relations info
            _relations = self.relations
            _column_names_in_relations = {
                table
                for relation in _relations or ()
                for table in (relation.from_, relation.to)
            }
            _tables_names_in_relations = {
                column_name.split(".")[0]
                for column_name in _column_names_in_relations or ()
            }

            if not self.relations:
                raise ValueError("At least one relation must be defined for view.")

            if not all(
                is_view_column_name(column_name) for column_name in _column_names
            ):
                raise ValueError(
                    "All columns in a view must be in the format '[table].[column]'."
                )

            if not all(
                is_view_column_name(column_name)
                for column_name in _column_names_in_relations
            ):
                raise ValueError(
                    "All params 'from' and 'to' in the relations must be in the format '[table].[column]'."
                )

            if (
                uncovered_tables := _tables_names_in_columns
                - _tables_names_in_relations
            ):
                raise ValueError(
                    f"No relations provided for the following tables {uncovered_tables}."
                )

        elif any(is_view_column_name(column_name) for column_name in _column_names):
            raise ValueError("All columns in a table must be in the format '[column]'.")
        return self

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), sort_keys=False)


def is_schema_source_same(
    schema1: SemanticLayerSchema, schema2: SemanticLayerSchema
) -> bool:
    source1 = schema1.source
    source2 = schema2.source

    return source1.type == source2.type and json.dumps(
        source1.connection, sort_keys=True
    ) == json.dumps(source2.connection, sort_keys=True)
