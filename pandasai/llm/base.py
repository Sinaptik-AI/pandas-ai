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

import ast
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import openai
import requests

from ..constants import END_CODE_TAG, START_CODE_TAG
from ..exceptions import (
    APIKeyNotFoundError,
    MethodNotImplementedError,
    NoCodeFoundError,
)
from ..helpers._optional import import_dependency
from ..helpers.openai_info import openai_callback_var
from ..prompts.base import Prompt


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
            code (str): Code

        Returns:
            str: Polished code
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
        match = re.search(
            rf"{START_CODE_TAG}(.*)({END_CODE_TAG}"
            rf"|{END_CODE_TAG.replace('<', '</')}"
            rf"|{START_CODE_TAG.replace('<', '</')})",
            code,
            re.DOTALL,
        )
        if match:
            code = match.group(1).strip()
        if len(code.split(separator)) > 1:
            code = code.split(separator)[1]
        code = self._polish_code(code)
        if not self._is_python_code(code):
            raise NoCodeFoundError("No code found in the response")

        return code

    @abstractmethod
    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        """
        Execute the LLM with given prompt.

        Args:
            instruction (Prompt): Prompt
            value (str): Value
            suffix (str, optional): Suffix. Defaults to "".

        Raises:
            MethodNotImplementedError: Call method has not been implemented
        """
        raise MethodNotImplementedError("Call method has not been implemented")

    def generate_code(self, instruction: Prompt, prompt: str) -> str:
        """
        Generate the code based on the instruction and the given prompt.

        Returns:
            str: Code
        """
        return self._extract_code(self.call(instruction, prompt, suffix="\n\nCode:\n"))


class BaseOpenAI(LLM, ABC):
    """Base class to implement a new OpenAI LLM
    LLM base class, this class is extended to be used with OpenAI API.

    """

    api_token: str
    temperature: float = 0
    max_tokens: int = 512
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

        Returns: None

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

        Returns (Dict): A dict of OpenAi API parameters

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
            prompt (str): Prompt

        Returns:
            str: LLM response
        """
        params = {**self._default_params, "prompt": prompt}

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = openai.Completion.create(**params)

        openai_handler = openai_callback_var.get()
        if openai_handler:
            openai_handler(response)

        return response["choices"][0]["text"]

    def chat_completion(self, value: str) -> str:
        """
        Query the chat completion API

        Args:
            value (str): Prompt

        Returns:
            str: LLM response
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

        openai_handler = openai_callback_var.get()
        if openai_handler:
            openai_handler(response)

        return response["choices"][0]["message"]["content"]


class HuggingFaceLLM(LLM):
    """Base class to implement a new Hugging Face LLM.

    LLM base class is extended to be used with HuggingFace LLM Modes APIs

    """

    last_prompt: Optional[str] = None
    api_token: str
    _api_url: str = "https://api-inference.huggingface.co/models/"
    _max_retries: int = 3

    @property
    def type(self) -> str:
        return "huggingface-llm"

    def query(self, payload):
        """
        Query the HF API
        Args:
            payload: A JSON form payload

        Returns: Generated Response

        """

        headers = {"Authorization": f"Bearer {self.api_token}"}

        response = requests.post(
            self._api_url, headers=headers, json=payload, timeout=60
        )

        return response.json()[0]["generated_text"]

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        """
        A call method of HuggingFaceLLM class.
        Args:
            instruction (object): A prompt object
            value (str):
            suffix (str):

        Returns (str): A string response

        """

        prompt = str(instruction)
        payload = prompt + value + suffix

        # sometimes the API doesn't return a valid response, so we retry passing the
        # output generated from the previous call as the input
        for _i in range(self._max_retries):
            response = self.query({"inputs": payload})
            payload = response
            if response.count("<endCode>") >= 2:
                break

        # replace instruction + value from the inputs to avoid showing it in the output
        output = response.replace(prompt + value + suffix, "")
        ans = ""
        for line in output.split("\n"):
            if line.find("utput:") != -1:
                break
            if ans == "":
                ans = ans + line
            else:
                ans = ans + "\n" + line
        if len(ans.split("'''")) > 0:
            ans = ans.split("'''")[0]
        output = ans
        return output


class BaseGoogle(LLM):
    """Base class to implement a new Google LLM

    LLM base class is extended to be used with Google Palm API.
    """

    genai: Any
    temperature: Optional[float] = 0
    top_p: Optional[float] = 0.8
    top_k: Optional[float] = 0.3
    max_output_tokens: Optional[int] = 1000

    def _configure(self, api_key: str):
        """
        Configure Google Palm API Key
        Args:
            api_key (str): A string of API keys generated from Google Cloud

        Returns:

        """

        if not api_key:
            raise APIKeyNotFoundError("Google Palm API key is required")

        err_msg = "Install google-generativeai >= 0.1 for Google Palm API"
        genai = import_dependency("google.generativeai", extra=err_msg)

        genai.configure(api_key=api_key)
        self.genai = genai

    def _configurevertexai(self, project_id: str, location: str):
        """
        Configure Google VertexAi
        Args:
            project_id: GCP Project
            location: Location of Project

        Returns: Vertexai Object

        """

        err_msg = "Install google-cloud-aiplatform for Google Vertexai"
        vertexai = import_dependency("vertexai", extra=err_msg)
        vertexai.init(project=project_id, location=location)
        self.vertexai = vertexai

    def _valid_params(self):
        return ["temperature", "top_p", "top_k", "max_output_tokens"]

    def _set_params(self, **kwargs):
        """
        Set Parameters
        Args:
            **kwargs: ["temperature", "top_p", "top_k", "max_output_tokens"]

        Returns:

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

        if self.top_k is not None and not 0 <= self.top_k <= 1:
            raise ValueError("top_k must be in the range [0.0, 1.0]")

        if self.max_output_tokens is not None and self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be greater than zero")

    @abstractmethod
    def _generate_text(self, prompt: str) -> str:
        """
        Generates text for prompt, specific to implementation.

        Args:
            prompt (str): Prompt

        Returns:
            str: LLM response
        """
        raise MethodNotImplementedError("method has not been implemented")

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        """
        Call the Google LLM.

        Args:
            instruction (object): Instruction to pass
            value (str): Value to pass
            suffix (str): Suffix to pass

        Returns:
            str: Response
        """
        self.last_prompt = str(instruction) + value
        prompt = str(instruction) + value + suffix
        return self._generate_text(prompt)
