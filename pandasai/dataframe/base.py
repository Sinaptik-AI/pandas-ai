from __future__ import annotations

import hashlib
import os
import re
from io import BytesIO
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Union
from zipfile import ZipFile

import pandas as pd
import yaml
from pandas._typing import Axes, Dtype

import pandasai as pai
from pandasai.config import Config
from pandasai.core.response import BaseResponse
from pandasai.data_loader.semantic_layer_schema import (
    Column,
    Destination,
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

        self.description: Optional[str] = kwargs.pop("description", None)
        self.path: Optional[str] = kwargs.pop("path", None)
        schema: Optional[SemanticLayerSchema] = kwargs.pop("schema", None)

        self.schema = schema
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

    @staticmethod
    def _create_yml_template(
        name, description, columns_dict: List[dict]
    ) -> Dict[str, Any]:
        """
        Generate a .yml file with a simplified metadata template from a pandas DataFrame.

        Args:
            name: dataset name
            description: dataset description
            columns_dict: dictionary with info about columns of the dataframe
        """

        if columns_dict:
            columns_dict = list(map(lambda column: Column(**column), columns_dict))

        schema = SemanticLayerSchema(
            name=name,
            description=description,
            columns=columns_dict,
            source=Source(type="parquet", path="data.parquet"),
            destination=Destination(
                type="local", format="parquet", path="data.parquet"
            ),
        )

        return schema.to_dict()

    def save(
        self, path: str, name: str, description: str = None, columns: List[dict] = None
    ):
        self.name = name
        self.description = description

        # Validate path format
        path_parts = path.split("/")
        if len(path_parts) != 2:
            raise ValueError("Path must be in format 'organization/dataset'")

        org_name, dataset_name = path_parts
        if not org_name or not dataset_name:
            raise ValueError("Both organization and dataset names are required")

        # Validate organization and dataset name format
        if not bool(re.match(r"^[a-z0-9\-_]+$", org_name)):
            raise ValueError(
                "Organization name must be lowercase and use hyphens instead of spaces (e.g. 'my-org')"
            )

        if not bool(re.match(r"^[a-z0-9\-_]+$", dataset_name)):
            raise ValueError(
                "Dataset name must be lowercase and use hyphens instead of spaces (e.g. 'my-dataset')"
            )

        self.path = path

        # Create full path with slugified dataset name
        dataset_directory = os.path.join(
            find_project_root(), "datasets", org_name, dataset_name
        )

        os.makedirs(dataset_directory, exist_ok=True)

        # Convert to pandas DataFrame while preserving all data
        df = pd.DataFrame(self._data)
        df.to_parquet(os.path.join(dataset_directory, "data.parquet"), index=False)

        # create schema yaml file
        schema_path = os.path.join(dataset_directory, "schema.yaml")
        self.schema = self._create_yml_template(self.name, self.description, columns)
        # Save metadata to a .yml file
        with open(schema_path, "w") as yml_file:
            yaml.dump(self.schema, yml_file, sort_keys=False)

        print(f"Dataset saved successfully to path: {dataset_directory}")

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
            raise PandaAIApiKeyError(
                "Set PANDABI_API_URL and PANDABI_API_KEY in environment to pull dataset to the remote server"
            )

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
        df = dataset_loader.load(self.path, virtualized=not isinstance(self, DataFrame))
        self.__init__(
            df, schema=df.schema, name=df.name, description=df.description, path=df.path
        )

        print(f"Dataset pulled successfully from path: {self.path}")

    def execute_sql_query(self, query: str) -> pd.DataFrame:
        import duckdb

        db = duckdb.connect(":memory:")
        db.register(self.name, self)
        return db.query(query).df()
