import requests
import os
from dotenv import load_dotenv
from .base import LLM

load_dotenv()


class OpenAssistant(LLM):
    api_token: str

    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_KEY")
        if self.api_token is None:
            raise Exception("HuggingFace Hub API key is required")

    def query(self, payload):
        API_URL = "https://api-inference.huggingface.co/models/OpenAssistant/oasst-sft-1-pythia-12b"
        headers = {"Authorization": "Bearer {}".format(self.api_token)}

        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    def call(self, instruction: str, input: str) -> str:
        output = self.query(
            {"inputs": "<|prompter|>" + instruction + input + "<|endoftext|>"}
        )
        return output[0]["generated_text"]

    @property
    def _type(self) -> str:
        return "open-assistant"
