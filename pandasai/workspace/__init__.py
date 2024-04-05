import base64
import json
from typing import List, Optional, Union

import pandas as pd
import requests
from pandasai.connectors.airtable import AirtableConnector
from pandasai.connectors.pandas import PandasConnector
from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
)
from pandasai.ee.connectors.google_big_query import GoogleBigQueryConnector

from pandasai.exceptions import PandasAIDatasetUploadFailed
from pandasai.helpers.logger import Logger
from pandasai.helpers.request import Session
from pandasai.workspace.response_desrializer import ResponseDeserializer


class Workspace:
    """
    Workspace allows you to create workspace and start chating
    """

    name: str
    _id: str
    _conversation_id: str
    _verbose: bool
    _last_code_generated: str

    def __init__(
        self,
        slug: str,
        conversation_id: str = None,
        endpoint_url: Optional[str] = None,
        api_key: Optional[str] = None,
        logger: Optional[Logger] = None,
        verbose: bool = True,
    ):
        self._session = Session(endpoint_url, api_key, logger)
        self._logger = logger or Logger()
        self.name = slug

        # initialize workspace
        data = self._session.post("/spaces/initialize", json={"slug": slug})
        self._id = data["data"]["id"]
        self._conversation_id = conversation_id
        self._verbose = verbose

    def chat(self, query: str) -> List[dict]:
        """
        Chat with assistant on the datasets in workspace
        """
        data = self._session.post(
            "/chat",
            json={
                "space_id": self._id,
                "query": query,
                "conversation_id": self._conversation_id,
            },
        )["data"]

        if "conversation_id" in data:
            self._conversation_id = data["conversation_id"]
        else:
            return data

        if "code" in data:
            self._last_code_generated = data["code"]

        response = ResponseDeserializer.deserialize(data["response"])

        if self._verbose:
            self._print_response(response)

        return response

    def push(
        self,
        connector: Union[pd.DataFrame, SQLConnector],
        name: str,
        description: str = "",
    ):
        """
        Add dataframe to the workspace
        Args:
            df (pd.DataFrame): upload dataset to the workspace
            name (str): unique name for dataset in space
            description (str, optional): description. Defaults to "".

        Raises:
            PandasAIDatasetUploadFailed: on upload failure
        """
        if isinstance(connector, (pd.DataFrame, PandasConnector)):
            df = connector
            if isinstance(connector, PandasConnector):
                df = connector.pandas_df

            # Prepare dataset upload
            data = self._session.post(
                "/table", json={"name": name, "description": description}
            )["data"]

            csv_content = df.to_csv(index=False).encode("utf-8")

            form_data = dict(data.get("upload_url", {}).get("fields", {}))
            files = {"file": csv_content}

            # Upload file
            response_csv_data = requests.post(
                data.get("upload_url", {}).get("url", ""), data=form_data, files=files
            )

            if response_csv_data.status_code not in [204, 200]:
                raise PandasAIDatasetUploadFailed("Failed to push dataset!")

            # Add file to space
            self._session.post(
                "/table/file-uploaded",
                json={"space_id": self._id, "dataframe_id": data["id"]},
            )
        elif isinstance(connector, GoogleBigQueryConnector):
            if connector.config.credentials_path:
                files = {"file": open(connector.config.credentials_path, "rb")}

            elif connector.config.credentials_base64:
                decodebytes_str = base64.b64decode(connector.config.credentials_base64)
                # decoded_string = connector.config.credentials_base64.decode('utf-8')
                files = {"file": ("credentials.json", decodebytes_str)}

            data = {
                "name": name,
                "type": self._get_connector_name(connector),
                "description": description,
                "config": connector.config.json(),
                "space_id": self._id,
            }

            headers = {
                "Authorization": f"Bearer {self._session._api_key}",
            }

            self._session.post(
                "/connector/add", data=data, files=files, headers=headers
            )
        elif isinstance(connector, (SQLConnector, AirtableConnector)):
            config_json = json.loads(connector.config.json())
            del config_json["where"]
            data = {
                "name": name,
                "type": self._get_connector_name(connector),
                "description": description,
                "config": json.dumps(config_json),
                "space_id": self._id,
            }
            self._session.post("/connector/add", json=data)

        self._logger.log(f"Dataframe {name} successfully added!")

    def _get_connector_name(self, connector):
        return (
            "PostgresConnector"
            if isinstance(connector, PostgreSQLConnector)
            else connector.__class__.__name__
        )

    def _print_response(self, response: List[dict]) -> None:
        """
        Prints the chat response received
        """
        for output in response:
            print(output["value"])

    @property
    def last_code_generated(self):
        return self._last_code_generated

    @property
    def conversation_id(self):
        return self._conversation_id
