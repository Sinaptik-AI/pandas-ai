""" Base class to implement a new Hugging Face LLM. """

from typing import Optional

import requests

from .base import LLM


class HuggingFaceLLM(LLM):
    """Base class to implement a new Hugging Face LLM."""

    last_prompt: Optional[str] = None
    api_token: str
    _api_url: str = "https://api-inference.huggingface.co/models/"
    _max_retries: int = 3

    @property
    def type(self) -> str:
        return "huggingface-llm"

    def query(self, payload):
        """Query the API"""

        headers = {"Authorization": f"Bearer {self.api_token}"}

        response = requests.post(
            self._api_url, headers=headers, json=payload, timeout=60
        )

        return response.json()[0]["generated_text"]

    def call(self, instruction: str, value: str, suffix: str = "") -> str:
        """Call the LLM"""

        payload = instruction + value + suffix

        # sometimes the API doesn't return a valid response, so we retry passing the
        # output generated from the previous call as the input
        for _i in range(self._max_retries):
            response = self.query({"inputs": payload})
            payload = response
            if response.count("<endCode>") >= 2:
                break

        # replace instruction + value from the inputs to avoid showing it in the output
        output = response.replace(instruction + value + suffix, "")
        return output
