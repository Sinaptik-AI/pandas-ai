"""Google VertexAI

This module is to run the Google VertexAI LLM.
To read more on VertexAI:
https://cloud.google.com/vertex-ai/docs/generative-ai/learn/generative-ai-studio.

Example:
    Use below example to call Google VertexAI

    >>> from pandasai.llm.google_palm import GoogleVertexAI

"""
from typing import Optional

from pandasai.helpers.memory import Memory

from ..exceptions import UnsupportedModelError
from ..helpers.optional import import_dependency
from .base import BaseGoogle


class GoogleVertexAI(BaseGoogle):
    """Google Palm Vertexai LLM
    BaseGoogle class is extended for Google Palm model using Vertexai.
    The default model support at the moment is text-bison-001.
    However, user can choose to use code-bison-001 too.
    """

    _supported_code_models = [
        "code-bison",
        "code-bison-32k",
        "code-bison-32k@002",
        "code-bison@001",
        "code-bison@002",
    ]
    _supported_text_models = [
        "text-bison",
        "text-bison-32k",
        "text-bison-32k@002",
        "text-bison@001",
        "text-bison@002",
        "text-unicorn@001",
    ]
    _supported_generative_models = [
        "gemini-pro",
    ]
    _supported_code_chat_models = ["codechat-bison@001", "codechat-bison@002"]

    def __init__(
        self, project_id: str, location: str, model: Optional[str] = None, **kwargs
    ):
        """
        A init class to implement the Google Vertexai Models

        Args:
            project_id (str): GCP project
            location (str): GCP project Location
            model Optional (str): Model to use Default to text-bison@001
            **kwargs: Arguments to control the Model Parameters
        """

        self.model = model or "text-bison@001"

        self._configure(project_id, location)
        self.project_id = project_id
        self.location = location
        self._set_params(**kwargs)

    def _configure(self, project_id: str, location: str):
        """
        Configure Google VertexAi. Set value `self.vertexai` attribute.

        Args:
            project_id (str): GCP Project.
            location (str): Location of Project.

        Returns:
            None.

        """

        err_msg = "Install google-cloud-aiplatform for Google Vertexai"
        vertexai = import_dependency("vertexai", extra=err_msg)
        vertexai.init(project=project_id, location=location)
        self.vertexai = vertexai

    def _valid_params(self):
        """Returns if the Parameters are valid or Not"""
        return super()._valid_params() + ["model"]

    def _validate(self):
        """
        A method to Validate the Model

        """

        super()._validate()

        if not self.model:
            raise ValueError("model is required.")

    def _generate_text(self, prompt: str, memory: Optional[Memory] = None) -> str:
        """
        Generates text for prompt.

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        self._validate()

        updated_prompt = self.prepend_system_prompt(prompt, memory)

        self.last_prompt = updated_prompt

        if self.model in self._supported_code_models:
            from vertexai.preview.language_models import CodeGenerationModel

            code_generation = CodeGenerationModel.from_pretrained(self.model)

            completion = code_generation.predict(
                prefix=prompt,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            )
        elif self.model in self._supported_text_models:
            from vertexai.preview.language_models import TextGenerationModel

            text_generation = TextGenerationModel.from_pretrained(self.model)

            completion = text_generation.predict(
                prompt=updated_prompt,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=self.max_output_tokens,
            )
        elif self.model in self._supported_generative_models:
            from vertexai.preview.generative_models import GenerativeModel

            model = GenerativeModel(self.model)

            responses = model.generate_content(
                [updated_prompt],
                generation_config={
                    "max_output_tokens": self.max_output_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                },
            )

            completion = responses.candidates[0].content.parts[0]
        elif self.model in self._supported_code_chat_models:
            from vertexai.language_models import ChatMessage, CodeChatModel

            code_chat_model = CodeChatModel.from_pretrained(self.model)
            messages = []

            for message in memory.all():
                if message["is_user"]:
                    messages.append(
                        ChatMessage(author="user", content=message["message"])
                    )
                else:
                    messages.append(
                        ChatMessage(author="model", content=message["message"])
                    )
            chat = code_chat_model.start_chat(
                context=memory.get_system_prompt(), message_history=messages
            )

            response = chat.send_message(prompt)
            return response.text

        else:
            raise UnsupportedModelError(self.model)

        return completion.text

    @property
    def type(self) -> str:
        return "google-vertexai"
