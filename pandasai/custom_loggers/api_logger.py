import logging
from typing import Union
import requests
from pandasai.helpers.logger import Logger


class APILogger(Logger):
    _api_key: str = None
    _server_url: str = None

    def __init__(self, server_url: str, api_key: str):
        self._api_key = api_key
        self._server_url = server_url

    def log(self, message: Union[str, dict], level: int = logging.INFO):
        try:
            if isinstance(message, dict):
                log_data = {
                    "api_key_id": self._api_key,
                    "json_log": message,
                }
                response = requests.post(
                    f"{self._server_url}/api/log/add", json=log_data
                )
                if response.status_code != 200:
                    raise Exception(response.text)

        except Exception as e:
            print(f"Exception in APILogger: {e}")
