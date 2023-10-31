""" Base class to implement a new LLM

This module is the base class to integrate the various LLMs API. This module also
includes the Base LLM classes for OpenAI, HuggingFace and Google PaLM.

Example:

    ```
    from .base import BaseOpenAI

    class CustomLLM(BaseOpenAI):

        Custom Class Starts here!!
    ```
"""

import os
import ast
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import openai
import requests

from ..exceptions import (
    APIKeyNotFoundError,
    MethodNotImplementedError,
    NoCodeFoundError,
    LLMResponseHTTPError,
)
from ..helpers.openai_info import openai_callback_var
from ..prompts.base import AbstractPrompt


class LLM:
    """Base class to implement a new LLM."""

    last_prompt: Optional[str] = None

    def is_pandasai_llm(self) -> bool:
        """
        Return True if the LLM is from pandasAI.

        Returns:
            bool: True if the LLM is from pandasAI

        """
        return True

    @property
    def type(self) -> str:
        """
        Return type of LLM.

        Raises:
            APIKeyNotFoundError: Type has not been implemented

        Returns:
            str: Type of LLM a string

        """
        raise APIKeyNotFoundError("Type has not been implemented")

    def _polish_code(self, code: str) -> str:
        """
        Polish the code by removing the leading "python" or "py",  \
        removing the imports and removing trailing spaces and new lines.

        Args:
            code (str): A sting of Python code.

        Returns:
            str: Polished code.

        """
        if re.match(r"^(python|py)", code):
            code = re.sub(r"^(python|py)", "", code)
        if re.match(r"^`.*`$", code):
            code = re.sub(r"^`(.*)`$", r"\1", code)
        code = code.strip()
        return code

    def _is_python_code(self, string):
        """
        Return True if it is valid python code.
        Args:
            string (str):

        Returns (bool): True if Python Code otherwise False

        """
        try:
            ast.parse(string)
            return True
        except SyntaxError:
            return False

    def _extract_code(self, response: str, separator: str = "```") -> str:
        """
        Extract the code from the response.

        Args:
            response (str): Response
            separator (str, optional): Separator. Defaults to "```".

        Raises:
            NoCodeFoundError: No code found in the response

        Returns:
            str: Extracted code from the response

        """
        code = response
        if len(code.split(separator)) > 1:
            code = code.split(separator)[1]
        code = self._polish_code(code)
        if not self._is_python_code(code):
            raise NoCodeFoundError("No code found in the response")

        return code

    def _extract_tag_text(self, response: str, tag: str) -> str:
        """
        Extracts the text between two tags in the response.

        Args:
            response (str): Response
            tag (str): Tag name

        Returns:
            (str or None): Extracted text from the response
        """

        if match := re.search(
            f"(<{tag}>)(.*)(</{tag}>)",
            response,
            re.DOTALL | re.MULTILINE,
        ):
            return match[2]
        return None

    def _extract_reasoning(self, response: str) -> str:
        """
        Extracts the reasoning from the response (wrapped in <reasoning> tags).

        Args:
            response (str): Response

        Returns:
            (str or None): Extracted reasoning from the response
        """

        return self._extract_tag_text(response, "reasoning")

    def _extract_answer(self, response: str) -> str:
        """
        Extracts the answer from the response (wrapped in <answer> tags).

        Args:
            response (str): Response

        Returns:
            (str or None): Extracted answer from the response
        """

        sentences = [
            sentence
            for sentence in response.split(". ")
            if "temp_chart.png" not in sentence
        ]
        answer = ". ".join(sentences)

        return self._extract_tag_text(answer, "answer")

    @abstractmethod
    def call(self, instruction: AbstractPrompt, suffix: str = "") -> str:
        """
        Execute the LLM with given prompt.

        Args:
            instruction (AbstractPrompt): A prompt object with instruction for LLM.
            suffix (str, optional): Suffix. Defaults to "".

        Raises:
            MethodNotImplementedError: Call method has not been implemented

        """
        raise MethodNotImplementedError("Call method has not been implemented")

    def generate_code(self, instruction: AbstractPrompt) -> [str, str, str]:
        """
        Generate the code based on the instruction and the given prompt.

        Args:
            instruction (AbstractPrompt): Prompt with instruction for LLM.

        Returns:
            str: A string of Python code.

        """
        response = self.call(instruction, suffix="")
        return [
            self._extract_code(response),
            self._extract_reasoning(response),
            self._extract_answer(response),
        ]


class BaseOpenAI(LLM, ABC):
    """Base class to implement a new OpenAI LLM.

    LLM base class, this class is extended to be used with OpenAI API.

    """

    api_token: str
    temperature: float = 0
    max_tokens: int = 1000
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0.6
    stop: Optional[str] = None
    # support explicit proxy for OpenAI
    openai_proxy: Optional[str] = None

    def _set_params(self, **kwargs):
        """
        Set Parameters
        Args:
            **kwargs: ["model", "engine", "deployment_id", "temperature","max_tokens",
            "top_p", "frequency_penalty", "presence_penalty", "stop", ]

        Returns:
            None.

        """

        valid_params = [
            "model",
            "engine",
            "deployment_id",
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

    @property
    def _default_params(self) -> Dict[str, Any]:
        """
        Get the default parameters for calling OpenAI API

        Returns
            Dict: A dict of OpenAi API parameters.

        """

        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }

    def completion(self, prompt: str) -> str:
        """
        Query the completion API

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        params = {**self._default_params, "prompt": prompt}

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = openai.Completion.create(**params)

        if openai_handler := openai_callback_var.get():
            openai_handler(response)

        return response["choices"][0]["text"]

    def chat_completion(self, value: str) -> str:
        """
        Query the chat completion API

        Args:
            value (str): Prompt

        Returns:
            str: LLM response.

        """
        params = {
            **self._default_params,
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

        if openai_handler := openai_callback_var.get():
            openai_handler(response)

        return response["choices"][0]["message"]["content"]


class HuggingFaceLLM(LLM):
    """Base class to implement a new Hugging Face LLM.

    LLM base class is extended to be used with HuggingFace LLM Modes APIs.

    """

    last_prompt: Optional[str] = None
    api_token: str
    _api_url: str = "https://api-inference.huggingface.co/models/"
    _max_retries: int = 3

    @property
    def type(self) -> str:
        return "huggingface-llm"

    def _setup(self, **kwargs):
        """
        Setup the HuggingFace LLM

        Args:
            **kwargs: ["api_token", "max_retries"]

        """
        self.api_token = (
            kwargs.get("api_token") or os.getenv("HUGGINGFACE_API_KEY") or None
        )
        if self.api_token is None:
            raise APIKeyNotFoundError("HuggingFace Hub API key is required")

        # Since the huggingface API only returns few tokens at a time, we need to
        # call the API multiple times to get all the tokens. This is the maximum
        # number of retries we will do.
        if kwargs.get("max_retries"):
            self._max_retries = kwargs.get("max_retries")

    def __init__(self, **kwargs):
        """
        __init__ method of HuggingFaceLLM Class

        Args:
            **kwargs: ["api_token", "max_retries"]

        """
        self._setup(**kwargs)

    def query(self, payload) -> str:
        """
        Query the HF API
        Args:
            payload: A JSON form payload

        Returns:
            str: Value of the field "generated_text" in response JSON
                given by the remote server.

        Raises:
            LLMResponseHTTPError: If api-inference.huggingface.co responses
                with any error HTTP code (>= 400).

        """

        headers = {"Authorization": f"Bearer {self.api_token}"}

        response = requests.post(
            self._api_url, headers=headers, json=payload, timeout=60
        )

        if response.status_code >= 400:
            try:
                error_msg = response.json().get("error")
            except (requests.exceptions.JSONDecodeError, TypeError):
                error_msg = None

            raise LLMResponseHTTPError(
                status_code=response.status_code, error_msg=error_msg
            )

        return response.json()[0]["generated_text"]

    def call(self, instruction: AbstractPrompt, suffix: str = "") -> str:
        """
        A call method of HuggingFaceLLM class.
        Args:
            instruction (AbstractPrompt): A prompt object with instruction for LLM.
            suffix (str): A string representing the suffix to be truncated
                from the generated response.

        Returns
            str: LLM response.

        """

        prompt = instruction.to_string()
        payload = prompt + suffix

        # sometimes the API doesn't return a valid response, so we retry passing the
        # output generated from the previous call as the input
        for _i in range(self._max_retries):
            response = self.query({"inputs": payload})
            payload = response

            match = re.search(
                "(```python)(.*)(```)",
                response.replace(prompt + suffix, ""),
                re.DOTALL | re.MULTILINE,
            )
            if match:
                break

        return response.replace(prompt + suffix, "")


class BaseGoogle(LLM):
    """Base class to implement a new Google LLM

    LLM base class is extended to be used with
    """

    temperature: Optional[float] = 0
    top_p: Optional[float] = 0.8
    top_k: Optional[int] = 40
    max_output_tokens: Optional[int] = 1000

    def _valid_params(self):
        return ["temperature", "top_p", "top_k", "max_output_tokens"]

    def _set_params(self, **kwargs):
        """
        Dynamically set Parameters for the object.

        Args:
            **kwargs:
                Possible keyword arguments: "temperature", "top_p", "top_k",
                "max_output_tokens".

        Returns:
            None.

        """

        valid_params = self._valid_params()
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)

    def _validate(self):
        """Validates the parameters for Google"""

        if self.temperature is not None and not 0 <= self.temperature <= 1:
            raise ValueError("temperature must be in the range [0.0, 1.0]")

        if self.top_p is not None and not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be in the range [0.0, 1.0]")

        if self.top_k is not None and not 0 <= self.top_k <= 100:
            raise ValueError("top_k must be in the range [0.0, 100.0]")

        if self.max_output_tokens is not None and self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be greater than zero")

    @abstractmethod
    def _generate_text(self, prompt: str) -> str:
        """
        Generates text for prompt, specific to implementation.

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        raise MethodNotImplementedError("method has not been implemented")

    def call(self, instruction: AbstractPrompt, suffix: str = "") -> str:
        """
        Call the Google LLM.

        Args:
            instruction (AbstractPrompt): Instruction to pass.
            suffix (str): Suffix to pass. Defaults to an empty string ("").

        Returns:
            str: LLM response.

        """
        self.last_prompt = instruction.to_string() + suffix
        return self._generate_text(self.last_prompt)
