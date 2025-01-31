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


class SQLConnectionConfig(BaseModel):
    """
    Common connection configuration for MySQL and PostgreSQL.
    """

    host: str = Field(..., description="Host for the database server")
    port: int = Field(..., description="Port for the database server")
    database: str = Field(..., description="Target database name")
    user: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")


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


class TransformationParams(BaseModel):
    column: Optional[str] = Field(None, description="Column to transform")
    value: Optional[Union[str, int, float, bool]] = Field(
        None, description="Value for fill_na and other transformations"
    )
    mapping: Optional[Dict[str, str]] = Field(
        None, description="Mapping dictionary for map_values transformation"
    )
    format: Optional[str] = Field(None, description="Format string for date formatting")
    decimals: Optional[int] = Field(
        None, description="Number of decimal places for rounding"
    )
    factor: Optional[Union[int, float]] = Field(None, description="Scaling factor")
    to: Optional[str] = Field(None, description="Target timezone or format")
    errors: Optional[str] = Field(
        None, description="Error handling mode for numeric/datetime conversion"
    )
    old_value: Optional[Any] = Field(
        None, description="Old value for replace transformation"
    )
    new_value: Optional[Any] = Field(
        None, description="New value for replace transformation"
    )
    new_name: Optional[str] = Field(
        None, description="New name for column in rename transformation"
    )
    pattern: Optional[str] = Field(
        None, description="Pattern for extract transformation"
    )
    length: Optional[int] = Field(
        None, description="Length for truncate transformation"
    )
    add_ellipsis: Optional[bool] = Field(
        True, description="Whether to add ellipsis in truncate"
    )
    width: Optional[int] = Field(None, description="Width for pad transformation")
    side: Optional[str] = Field("left", description="Side for pad transformation")
    pad_char: Optional[str] = Field(" ", description="Character for pad transformation")
    lower: Optional[Union[int, float]] = Field(None, description="Lower bound for clip")
    upper: Optional[Union[int, float]] = Field(None, description="Upper bound for clip")
    bins: Optional[Union[int, List[Union[int, float]]]] = Field(
        None, description="Bins for binning"
    )
    labels: Optional[List[str]] = Field(None, description="Labels for bins")
    drop_first: Optional[bool] = Field(
        True, description="Whether to drop first category in encoding"
    )
    drop_invalid: Optional[bool] = Field(
        False, description="Whether to drop invalid values"
    )
    start_date: Optional[str] = Field(
        None, description="Start date for date range validation"
    )
    end_date: Optional[str] = Field(
        None, description="End date for date range validation"
    )
    country_code: Optional[str] = Field(
        "+1", description="Country code for phone normalization"
    )
    columns: Optional[List[str]] = Field(
        None, description="List of columns for multi-column operations"
    )
    keep: Optional[str] = Field("first", description="Which duplicates to keep")
    ref_df: Optional[Any] = Field(
        None, description="Reference DataFrame for foreign key validation"
    )
    ref_column: Optional[str] = Field(
        None, description="Reference column for foreign key validation"
    )
    drop_negative: Optional[bool] = Field(
        False, description="Whether to drop negative values"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_required_params(cls, values: dict) -> dict:
        """Validate that required parameters are present based on the transformation type"""
        # Get the transformation type from parent if it exists
        transform_type = values.get("_transform_type")

        if transform_type == "rename":
            if not values.get("new_name"):
                raise ValueError("rename transformation requires 'new_name' parameter")

        return values


class Transformation(BaseModel):
    type: str = Field(..., description="Type of transformation to be applied.")
    params: Optional[TransformationParams] = Field(
        None, description="Parameters for the transformation."
    )

    @field_validator("type")
    @classmethod
    def is_transformation_type_supported(cls, type: str) -> str:
        if type not in VALID_TRANSFORMATION_TYPES:
            raise ValueError(f"Unsupported transformation type: {type}")
        return type

    @model_validator(mode="before")
    @classmethod
    def set_transform_type(cls, values: dict) -> dict:
        """Set transformation type in params for validation"""
        if values.get("params") and values.get("type"):
            if isinstance(values["params"], dict):
                values["params"]["_transform_type"] = values["type"]
        return values


class Source(BaseModel):
    type: str = Field(..., description="Type of the data source.")
    path: Optional[str] = Field(None, description="Path of the local data source.")
    connection: Optional[SQLConnectionConfig] = Field(
        None, description="Connection object of the data source."
    )
    table: Optional[str] = Field(None, description="Table of the data source.")

    @model_validator(mode="before")
    @classmethod
    def validate_type_and_fields(cls, values):
        _type = values.get("type")
        path = values.get("path")
        table = values.get("table")
        connection = values.get("connection")

        if _type in LOCAL_SOURCE_TYPES:
            if not path:
                raise ValueError(
                    f"For local source type '{_type}', 'path' must be defined."
                )
            if not table:
                raise ValueError(
                    f"For local source type '{_type}', 'table' must be defined."
                )

        elif _type in REMOTE_SOURCE_TYPES:
            if not connection:
                raise ValueError(
                    f"For remote source type '{_type}', 'connection' must be defined."
                )
            if not table:
                raise ValueError(
                    f"For remote source type '{_type}', 'table' must be defined."
                )
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
    source: Optional[Source] = Field(None, description="Data source for your dataset.")
    view: Optional[bool] = Field(None, description="Whether table is a view")
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

        if self.source and self.view:
            raise ValueError("Only one of 'source' or 'view' can be defined.")
        if not self.source and not self.view:
            raise ValueError("Either 'source' or 'view' must be defined.")

        if self.view:
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
                    "All columns in a view must be in the format '[dataset].[column]'."
                )

            if not all(
                is_view_column_name(column_name)
                for column_name in _column_names_in_relations
            ):
                raise ValueError(
                    "All params 'from' and 'to' in the relations must be in the format '[dataset].[column]'."
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
        return self.model_dump(exclude_none=True, by_alias=True)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), sort_keys=False)


def is_schema_source_same(
    schema1: SemanticLayerSchema, schema2: SemanticLayerSchema
) -> bool:
    source1 = schema1.source
    source2 = schema2.source

    return source1.type == source2.type and source1.path == source2.path
