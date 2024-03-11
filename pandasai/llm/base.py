""" Base class to implement a new LLM

This module is the base class to integrate the various LLMs API. This module also
includes the Base LLM classes for OpenAI and Google PaLM.

Example:

    ```
    from .base import BaseOpenAI

    class CustomLLM(BaseOpenAI):

        Custom Class Starts here!!
    ```
"""
from __future__ import annotations

import ast
import re
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Tuple, Union

from pandasai.helpers.memory import Memory
from pandasai.prompts.generate_system_message import GenerateSystemMessagePrompt

from ..exceptions import (
    APIKeyNotFoundError,
    MethodNotImplementedError,
    NoCodeFoundError,
)
from ..helpers.openai import is_openai_v1
from ..helpers.openai_info import openai_callback_var
from ..prompts.base import BasePrompt

if TYPE_CHECKING:
    from pandasai.pipelines.pipeline_context import PipelineContext


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
            code (str): A string of Python code.

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

    def prepend_system_prompt(self, prompt: BasePrompt, memory: Memory):
        """
        Append system prompt to the chat prompt, useful when model doesn't have messages for chat history
        Args:
            prompt (BasePrompt): prompt for chat method
            memory (Memory): user conversation history
        """
        return self.get_system_prompt(memory) + prompt if memory else prompt

    def get_system_prompt(self, memory: Memory) -> Any:
        """
        Generate system prompt with agent info and previous conversations
        """
        system_prompt = GenerateSystemMessagePrompt(memory=memory)
        return system_prompt.to_string()

    def get_messages(self, memory: Memory) -> Any:
        """
        Return formatted messages
        Args:
            memory (Memory): Get past Conversation from memory
        """
        return memory.get_previous_conversation()

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

    @abstractmethod
    def call(self, instruction: BasePrompt, context: PipelineContext = None) -> str:
        """
        Execute the LLM with given prompt.

        Args:
            instruction (BasePrompt): A prompt object with instruction for LLM.
            context (PipelineContext, optional): PipelineContext. Defaults to None.

        Raises:
            MethodNotImplementedError: Call method has not been implemented

        """
        raise MethodNotImplementedError("Call method has not been implemented")

    def generate_code(self, instruction: BasePrompt, context: PipelineContext) -> str:
        """
        Generate the code based on the instruction and the given prompt.

        Args:
            instruction (BasePrompt): Prompt with instruction for LLM.

        Returns:
            str: A string of Python code.

        """
        response = self.call(instruction, context)
        return self._extract_code(response)


class BaseOpenAI(LLM):
    """Base class to implement a new OpenAI LLM.

    LLM base class, this class is extended to be used with OpenAI API.

    """

    api_token: str
    api_base: str = "https://api.openai.com/v1"
    temperature: float = 0
    max_tokens: int = 1000
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0.6
    best_of: int = 1
    n: int = 1
    stop: Optional[str] = None
    request_timeout: Union[float, Tuple[float, float], Any, None] = None
    max_retries: int = 2
    seed: Optional[int] = None
    # support explicit proxy for OpenAI
    openai_proxy: Optional[str] = None
    default_headers: Union[Mapping[str, str], None] = None
    default_query: Union[Mapping[str, object], None] = None
    # Configure a custom httpx client. See the
    # [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
    http_client: Union[Any, None] = None
    client: Any
    _is_chat_model: bool

    def _set_params(self, **kwargs):
        """
        Set Parameters
        Args:
            **kwargs: ["model", "deployment_name", "temperature","max_tokens",
            "top_p", "frequency_penalty", "presence_penalty", "stop", "seed"]

        Returns:
            None.

        """

        valid_params = [
            "model",
            "deployment_name",
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "seed",
        ]
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        params: Dict[str, Any] = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "seed": self.seed,
            "stop": self.stop,
            "n": self.n,
        }

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens

        # Azure gpt-35-turbo doesn't support best_of
        # don't specify best_of if it is 1
        if self.best_of > 1:
            params["best_of"] = self.best_of

        return params

    @property
    def _invocation_params(self) -> Dict[str, Any]:
        """Get the parameters used to invoke the model."""
        openai_creds: Dict[str, Any] = {}
        if not is_openai_v1():
            openai_creds |= {
                "api_key": self.api_token,
                "api_base": self.api_base,
            }

        return {**openai_creds, **self._default_params}

    @property
    def _client_params(self) -> Dict[str, any]:
        return {
            "api_key": self.api_token,
            "timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
            "http_client": self.http_client,
        }

    def completion(self, prompt: str, memory: Memory) -> str:
        """
        Query the completion API

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        prompt = self.prepend_system_prompt(prompt, memory)

        params = {**self._invocation_params, "prompt": prompt}

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = self.client.create(**params)

        if openai_handler := openai_callback_var.get():
            openai_handler(response)

        self.last_prompt = prompt

        return response.choices[0].text

    def chat_completion(self, value: str, memory: Memory) -> str:
        """
        Query the chat completion API

        Args:
            value (str): Prompt

        Returns:
            str: LLM response.

        """
        messages = memory.to_openai_messages() if memory else []

        # adding current prompt as latest query message
        messages.append(
            {
                "role": "user",
                "content": value,
            },
        )

        params = {
            **self._invocation_params,
            "messages": messages,
        }

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = self.client.create(**params)

        if openai_handler := openai_callback_var.get():
            openai_handler(response)

        return response.choices[0].message.content

    def call(self, instruction: BasePrompt, context: PipelineContext = None):
        """
        Call the OpenAI LLM.

        Args:
            instruction (BasePrompt): A prompt object with instruction for LLM.
            context (PipelineContext): context to pass.

        Raises:
            UnsupportedModelError: Unsupported model

        Returns:
            str: Response
        """
        self.last_prompt = instruction.to_string()

        memory = context.memory if context else None

        return (
            self.chat_completion(self.last_prompt, memory)
            if self._is_chat_model
            else self.completion(self.last_prompt, memory)
        )


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
    def _generate_text(self, prompt: str, memory: Optional[Memory] = None) -> str:
        """
        Generates text for prompt, specific to implementation.

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        raise MethodNotImplementedError("method has not been implemented")

    def call(self, instruction: BasePrompt, context: PipelineContext = None) -> str:
        """
        Call the Google LLM.

        Args:
            instruction (BasePrompt): Instruction to pass.
            context (PipelineContext): Pass PipelineContext.

        Returns:
            str: LLM response.

        """
        self.last_prompt = instruction.to_string()
        memory = context.memory if context else None
        return self._generate_text(self.last_prompt, memory)
