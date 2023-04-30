""" Open Assistant LLM """

import os
import requests
from dotenv import load_dotenv
from .base import LLM
from ..exceptions import APIKeyNotFoundError

load_dotenv()


class OpenAssistant(LLM):
    """Open Assistant LLM"""

    api_token: str
    _api_url: str = (
        "https://api-inference.huggingface.co/models/"
        "OpenAssistant/oasst-sft-1-pythia-12b"
    )

    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_KEY")
        if self.api_token is None:
            raise APIKeyNotFoundError("HuggingFace Hub API key is required")

    def query(self, payload):
        """Query the API"""

        headers = {"Authorization": f"Bearer {self.api_token}"}

        response = requests.post(
            self._api_url, headers=headers, json=payload, timeout=60
        )
        return response.json()

    def call(self, instruction: str, value: str) -> str:
        output = self.query(
            {"inputs": "<|prompter|>" + instruction + value + "<|endoftext|>"}
        )
        return output[0]["generated_text"]

    @property
    def type(self) -> str:
        return "open-assistant"
