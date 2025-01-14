"""Request helper module."""

import logging
import os
import traceback
from typing import Optional
from urllib.parse import urljoin

import requests

from pandasai.exceptions import PandaAIApiCallError, PandaAIApiKeyError
from pandasai.helpers import load_dotenv
from pandasai.helpers.logger import Logger

load_dotenv()


class Session:
    _api_key: str
    _endpoint_url: str
    _logger: Logger

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        api_key: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        if api_key is None:
            api_key = os.environ.get("PANDABI_API_KEY") or None
        if api_key is None:
            raise PandaAIApiKeyError()
        self._api_key = api_key

        if endpoint_url is None:
            endpoint_url = os.environ.get("PANDABI_API_URL", "https://api.pandabi.ai")

        self._endpoint_url = endpoint_url
        self._version_path = "/api"
        self._logger = logger or Logger()

    def get(self, path=None, **kwargs):
        return self.make_request("GET", path, **kwargs)

    def post(self, path=None, **kwargs):
        return self.make_request("POST", path, **kwargs)

    def patch(self, path=None, **kwargs):
        return self.make_request("PATCH", path, **kwargs)

    def put(self, path=None, **kwargs):
        return self.make_request("PUT", path, **kwargs)

    def delete(self, path=None, **kwargs):
        return self.make_request("DELETE", path, **kwargs)

    def make_request(
        self,
        method,
        path,
        headers=None,
        params=None,
        data=None,
        json=None,
        timeout=300,
        **kwargs,
    ):
        try:
            url = urljoin(self._endpoint_url, self._version_path + path)
            if headers is None:
                headers = {
                    "x-authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",  # or any other headers you need
                }

            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=timeout,
                **kwargs,
            )

            try:
                data = response.json()
            except ValueError:
                if response.status_code == 200:
                    return response

            if response.status_code not in [200, 201]:
                if "message" in data:
                    raise PandaAIApiCallError(data["message"])
                elif "detail" in data:
                    raise PandaAIApiCallError(data["detail"])

            return data

        except requests.exceptions.RequestException as e:
            self._logger.log(f"Request failed: {traceback.format_exc()}", logging.ERROR)
            raise PandaAIApiCallError(f"Request failed: {e}") from e


def get_pandaai_session() -> Session:
    """Get a requests session with the PandaAI API key.

    Returns:
        requests.Session: Session with API key.
    """

    api_url = os.environ.get("PANDABI_API_URL", None)
    api_key = os.environ.get("PANDABI_API_KEY", None)
    if not api_url or not api_key:
        raise PandaAIApiKeyError(
            "Set PANDABI_API_URL and PANDABI_API_KEY in environment to push/pull dataset to the remote server"
        )

    return Session(endpoint_url=api_url, api_key=api_key)
