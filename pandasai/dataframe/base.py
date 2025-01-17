from __future__ import annotations

import hashlib
import os
from io import BytesIO
from typing import TYPE_CHECKING, ClassVar, Optional, Union
from zipfile import ZipFile

import pandas as pd
from pandas._typing import Axes, Dtype

import pandasai as pai
from pandasai.config import Config
from pandasai.core.response import BaseResponse
from pandasai.data_loader.semantic_layer_schema import (
    Column,
    SemanticLayerSchema,
    Source,
)
from pandasai.exceptions import DatasetNotFound, PandaAIApiKeyError
from pandasai.helpers.dataframe_serializer import DataframeSerializer
from pandasai.helpers.path import find_project_root
from pandasai.helpers.session import get_pandaai_session

if TYPE_CHECKING:
    from pandasai.agent.base import Agent


class DataFrame(pd.DataFrame):
    """
    PandaAI DataFrame that extends pandas DataFrame with natural language capabilities.

    Attributes:
        name (Optional[str]): Name of the dataframe
        description (Optional[str]): Description of the dataframe
        schema (Optional[SemanticLayerSchema]): Schema definition for the dataframe
        config (Config): Configuration settings
    """

    _metadata: ClassVar[list] = [
        "name",
        "description",
        "schema",
        "path",
        "config",
        "_agent",
        "_column_hash",
    ]

    def __init__(
        self,
        data=None,
        index: Axes | None = None,
        columns: Axes | None = None,
        dtype: Dtype | None = None,
        copy: bool | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            data=data, index=index, columns=columns, dtype=dtype, copy=copy
        )

        self.name: Optional[str] = kwargs.pop("name", None)
        self._column_hash = self._calculate_column_hash()

        if not self.name:
            self.name = f"table_{self._column_hash}"

        schema: Optional[SemanticLayerSchema] = kwargs.pop("schema", None)
        self.schema = schema or DataFrame.get_default_schema(self)

        self.description: Optional[str] = kwargs.pop("description", None)
        self.path: Optional[str] = kwargs.pop("path", None)
        self.config = pai.config.get()
        self._agent: Optional[Agent] = None

    def __repr__(self) -> str:
        """Return a string representation of the DataFrame."""
        name_str = f"name='{self.name}'" if self.name else ""
        desc_str = f"description='{self.description}'" if self.description else ""
        metadata = ", ".join(filter(None, [name_str, desc_str]))

        return f"PandaAI DataFrame({metadata})\n{super().__repr__()}"

    def _calculate_column_hash(self):
        column_string = ",".join(self.columns)
        return hashlib.md5(column_string.encode()).hexdigest()

    @property
    def column_hash(self):
        return self._column_hash

    @property
    def type(self) -> str:
        return "pd.DataFrame"

    def chat(
        self, prompt: str, config: Optional[Union[dict, Config]] = None
    ) -> BaseResponse:
        """
        Interact with the DataFrame using natural language.

        Args:
            prompt (str): The natural language query or instruction.
            config (Optional[Union[dict, Config]]): Configuration for the chat session.

        Returns:
            str: The response to the prompt.
        """
        if config:
            self.config = Config(**config) if isinstance(config, dict) else config

        if self._agent is None:
            from pandasai.agent import (
                Agent,
            )

            self._agent = Agent([self], config=self.config)

        return self._agent.chat(prompt)

    def follow_up(self, query: str, output_type: Optional[str] = None):
        if self._agent is None:
            raise ValueError(
                "No existing conversation. Please use chat() to start a new conversation."
            )
        return self._agent.follow_up(query, output_type)

    @property
    def rows_count(self) -> int:
        return len(self)

    @property
    def columns_count(self) -> int:
        return len(self.columns)

    def serialize_dataframe(self) -> str:
        """
        Serialize DataFrame to string representation.

        Returns:
            str: Serialized string representation of the DataFrame
        """
        return DataframeSerializer().serialize(self)

    def get_head(self):
        return self.head()

    def push(self):
        if self.path is None:
            raise ValueError(
                "Please save the dataset before pushing to the remote server."
            )

        api_key = os.environ.get("PANDABI_API_KEY", None)

        request_session = get_pandaai_session()

        params = {
            "path": self.path,
            "description": self.description,
            "name": self.name if self.name else "",
        }

        dataset_directory = os.path.join(find_project_root(), "datasets", self.path)

        headers = {"accept": "application/json", "x-authorization": f"Bearer {api_key}"}

        with open(
            os.path.join(dataset_directory, "schema.yaml"), "rb"
        ) as schema_file, open(
            os.path.join(dataset_directory, "data.parquet"), "rb"
        ) as data_file:
            files = [
                ("files", ("schema.yaml", schema_file, "application/x-yaml")),
                ("files", ("data.parquet", data_file, "application/octet-stream")),
            ]

            # Send the POST request
            request_session.post(
                "/datasets/push",
                files=files,
                params=params,
                headers=headers,
            )
            print("Your dataset was successfully pushed to the pandabi platform")

    def pull(self):
        api_key = os.environ.get("PANDABI_API_KEY", None)

        if not api_key:
            raise PandaAIApiKeyError()

        request_session = get_pandaai_session()

        headers = {"accept": "application/json", "x-authorization": f"Bearer {api_key}"}

        file_data = request_session.get(
            "/datasets/pull", headers=headers, params={"path": self.path}
        )
        if file_data.status_code != 200:
            raise DatasetNotFound("Remote dataset not found to pull!")

        with ZipFile(BytesIO(file_data.content)) as zip_file:
            for file_name in zip_file.namelist():
                target_path = os.path.join(
                    find_project_root(), "datasets", self.path, file_name
                )

                # Check if the file already exists
                if os.path.exists(target_path):
                    print(f"Replacing existing file: {target_path}")

                # Ensure target directory exists
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # Extract the file
                with open(target_path, "wb") as f:
                    f.write(zip_file.read(file_name))

        # Reloads the Dataframe
        from pandasai import DatasetLoader

        dataset_loader = DatasetLoader()
        df = dataset_loader.load(self.path)
        self.__init__(
            df, schema=df.schema, name=df.name, description=df.description, path=df.path
        )

        print(f"Dataset pulled successfully from path: {self.path}")

    @staticmethod
    def get_column_type(column_dtype) -> Optional[str]:
        """
        Map pandas dtype to a valid column type.
        """
        if pd.api.types.is_string_dtype(column_dtype):
            return "string"
        elif pd.api.types.is_integer_dtype(column_dtype):
            return "integer"
        elif pd.api.types.is_float_dtype(column_dtype):
            return "float"
        elif pd.api.types.is_datetime64_any_dtype(column_dtype):
            return "datetime"
        elif pd.api.types.is_bool_dtype(column_dtype):
            return "boolean"
        else:
            return None

    @classmethod
    def get_default_schema(cls, dataframe: DataFrame) -> SemanticLayerSchema:
        columns_list = [
            Column(name=str(name), type=DataFrame.get_column_type(dtype))
            for name, dtype in dataframe.dtypes.items()
        ]

        return SemanticLayerSchema(
            name=dataframe.name,
            source=Source(type="parquet", path="data.parquet"),
            columns=columns_list,
        )
