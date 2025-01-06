from __future__ import annotations
from io import BytesIO
import os
import re
from zipfile import ZipFile
import pandas as pd
from typing import TYPE_CHECKING, List, Optional, Union, Dict, ClassVar

import yaml


from pandasai.config import Config
import hashlib
from pandasai.exceptions import DatasetNotFound, PandasAIApiKeyError
from pandasai.helpers.dataframe_serializer import (
    DataframeSerializer,
    DataframeSerializerType,
)
from pandasai.helpers.path import find_project_root
from pandasai.helpers.request import get_pandaai_session
import pandasai as pai


if TYPE_CHECKING:
    from pandasai.agent.base import Agent


class DataFrame(pd.DataFrame):
    """
    PandasAI DataFrame that extends pandas DataFrame with natural language capabilities.

    Attributes:
        name (Optional[str]): Name of the dataframe
        description (Optional[str]): Description of the dataframe
        schema (Optional[Dict]): Schema definition for the dataframe
        config (Config): Configuration settings
    """

    _metadata: ClassVar[list] = [
        "name",
        "description",
        "filepath",
        "schema",
        "path",
        "config",
        "_agent",
        "_column_hash",
    ]

    def __init__(self, *args, **kwargs):
        self.name: Optional[str] = kwargs.pop("name", None)
        self.description: Optional[str] = kwargs.pop("description", None)
        self.path: Optional[str] = kwargs.pop("path", None)
        schema: Optional[Dict] = kwargs.pop("schema", None)

        super().__init__(*args, **kwargs)

        if schema is not None:
            self._validate_schema(schema)
        self.schema = schema
        self.config = pai.config.get()
        self._agent: Optional[Agent] = None
        self._column_hash = self._calculate_column_hash()

    def _validate_schema(self, schema: Optional[Dict]) -> None:
        """Validates the provided schema format."""
        if not isinstance(schema, dict):
            raise ValueError("Schema must be a dictionary")

    def __repr__(self) -> str:
        """Return a string representation of the DataFrame."""
        name_str = f"name='{self.name}'" if self.name else ""
        desc_str = f"description='{self.description}'" if self.description else ""
        metadata = ", ".join(filter(None, [name_str, desc_str]))

        print(f"Metadata: {metadata}")

        return f"PandasAI DataFrame({metadata})\n{super().__repr__()}"

    def _calculate_column_hash(self):
        column_string = ",".join(self.columns)
        return hashlib.md5(column_string.encode()).hexdigest()

    @property
    def column_hash(self):
        return self._column_hash

    def chat(self, prompt: str, config: Optional[Union[dict, Config]] = None) -> str:
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
            )  # Import here to avoid circular import

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

    def serialize_dataframe(
        self,
        index: int,
        is_direct_sql: bool,
        enforce_privacy: bool,
    ) -> str:
        """
        Serialize DataFrame to string representation.

        Args:
            index (int): Index of the dataframe
            is_direct_sql (bool): Whether the query is direct SQL
            serializer_type (DataframeSerializerType): Type of serializer to use
            enforce_privacy (bool): Whether to enforce privacy
            **kwargs: Additional parameters to pass to pandas to_string method

        Returns:
            str: Serialized string representation of the DataFrame
        """
        return DataframeSerializer().serialize(
            self,
            extras={
                "index": index,
                "type": "pd.DataFrame",
                "is_direct_sql": is_direct_sql,
                "enforce_privacy": enforce_privacy,
            },
            type_=DataframeSerializerType.CSV,
        )

    def get_head(self):
        return self.head()

    def _create_yml_template(self, name, description, columns: List[dict]):
        """
        Generate a .yml file with a simplified metadata template from a pandas DataFrame.

        Args:
            dataframe (pd.DataFrame): The DataFrame to document.
            description: dataset description
            output_yml_path (str): The file path where the .yml file will be saved.
            table_name (str): Name of the table or dataset.
        """
        # Metadata template
        return {
            "name": name,
            "description": description,
            "columns": columns,
            "source": {"type": "parquet", "path": "data.parquet"},
            "destination": {
                "type": "local",
                "format": "parquet",
                "path": "data.parquet",
            },
        }

    def save(
        self, path: str, name: str, description: str = None, columns: List[dict] = []
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
        api_key = os.environ.get("PANDASAI_API_KEY", None)

        request_session = get_pandaai_session()

        params = {
            "path": self.path,
            "description": self.description,
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
            return request_session.post(
                "/datasets/push",
                files=files,
                params=params,
                headers=headers,
            )

    def pull(self):
        api_key = os.environ.get("PANDASAI_API_KEY", None)

        if not api_key:
            raise PandasAIApiKeyError(
                "Set PANDASAI_API_URL and PANDASAI_API_KEY in environment to pull dataset to the remote server"
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

        # reloads the Dataframe
        from pandasai import DatasetLoader

        dataset_loader = DatasetLoader()
        df = dataset_loader.load(self.path, virtualized=not isinstance(self, DataFrame))
        self.__init__(
            df, schema=df.schema, name=df.name, description=df.description, path=df.path
        )
