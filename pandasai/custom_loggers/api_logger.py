import logging
import requests
from pandasai.helpers.logger import Logger


class APILogger(Logger):
    _api_key: str = None
    _server_url: str = None
    _user_id: str = None

    def __init__(self, server_url: str, user_id: str, api_key: str):
        self._api_key = api_key
        self._server_url = server_url
        self._user_id = user_id

    def log(self, message: str, level: int = logging.INFO):
        try:
            log_data = {
                # TODO - Remove user id from the API
                "user_id": self._user_id,
                "api_key_id": self._api_key,
                "json_log": message,
            }
            response = requests.post(f"{self._server_url}/api/log/add", json=log_data)
            if response.status_code != 200:
                raise Exception(response.text)
        except Exception:
            pass
