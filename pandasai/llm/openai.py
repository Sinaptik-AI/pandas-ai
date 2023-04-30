"""OpenAI LLM"""

import os
from dotenv import load_dotenv
import openai
from .base import LLM
from ..exceptions import APIKeyNotFoundError, UnsupportedOpenAIModelError

load_dotenv()


class OpenAI(LLM):
    """OpenAI LLM"""

    api_token: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0
    max_tokens: int = 512
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0.6
    stop: str = None

    def __init__(
        self,
        api_token: str = None,
        **kwargs,
    ):
        self.api_token = api_token or os.getenv("OPENAI_API_KEY")
        if self.api_token is None:
            raise APIKeyNotFoundError("OpenAI API key is required")
        openai.api_key = self.api_token

        self._set_params(**kwargs)

    def _set_params(self, **kwargs):
        valid_params = [
            "model",
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
        ]
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)

    def completion(self, prompt: str) -> str:
        """Query the completion API"""

        params = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = openai.Completion.create(**params)

        return response["choices"][0]["text"]

    def chat_completion(self, value: str) -> str:
        """Query the chat completion API"""

        params = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "messages": [
                {
                    "role": "system",
                    "content": value,
                }
            ],
        }

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = openai.ChatCompletion.create(**params)

        return response["choices"][0]["message"]["content"]

    def call(self, instruction: str, value: str) -> str:
        if self.model == "text-davinci-003":
            response = self.completion(str(instruction) + str(value))
        elif self.model == "gpt-3.5-turbo":
            response = self.chat_completion(str(instruction) + str(value))
        else:
            raise UnsupportedOpenAIModelError("Unsupported model")

        return response

    @property
    def type(self) -> str:
        return "openai"
