from typing import List, Optional

import pandas as pd
from pandasai.exceptions import PandasAIDatasetUploadFailed

from pandasai.helpers.logger import Logger
from pandasai.helpers.request import Session
from pandasai.workspace.response_desrializer import ResponseDeserializer
import requests


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
        self._conversation_id = None
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

        self._conversation_id = data["conversation_id"]
        if "code" in data:
            self._last_code_generated = data["code"]

        response = ResponseDeserializer.deserialize(data["response"])

        if self._verbose:
            self._print_response(response)

        return response

    def push(self, df: pd.DataFrame, name: str, description: str = ""):
        """
        Add dataframe to the workspace
        Args:
            df (pd.DataFrame): upload dataset to the workspace
            name (str): unique name for dataset in space
            description (str, optional): description. Defaults to "".

        Raises:
            PandasAIDatasetUploadFailed: on upload failure
        """
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
        self._logger.log(f"Dataframe {name} successfully added!")

    def _print_response(self, response: List[dict]) -> None:
        """
        Prints the chat response received
        """
        for output in response:
            print(output["value"])

    @property
    def last_code_generated(self):
        return self._last_code_generated
