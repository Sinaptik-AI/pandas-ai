"""Unit tests for the openai LLM class"""

import pytest

from pandasai.llm import GoogleVertexAI
from pandasai.exceptions import UnsupportedModelError


class MockedCompletion:
    def __init__(self, result: str):
        self.result = result


class TestGoogleVertexAI:
    def test_init_with_default_model(self, mocker):
        mocker.patch(
            "vertexai.preview.language_models.TextGenerationModel.from_pretrained",
            return_value="Test",
        )
        project_id = "your_project_id"
        location = "northamerica-northeast1"
        vertexai_instance = GoogleVertexAI(project_id, location)

        assert vertexai_instance.model == "text-bison@001"
        assert vertexai_instance.project_id == project_id
        assert vertexai_instance.location == location

    def test_init_with_custom_model(self, mocker):
        mocker.patch(
            "vertexai.preview.language_models.CodeGenerationModel.from_pretrained",
            return_value="Test",
        )
        project_id = "test-project"
        location = "northamerica-northeast1"
        custom_model = "code-bison@001"

        vertexai_instance = GoogleVertexAI(project_id, location, model=custom_model)

        assert vertexai_instance.model == custom_model
        assert vertexai_instance.project_id == project_id
        assert vertexai_instance.location == location

    def test_validate_with_model(self, mocker):
        mocker.patch(
            "vertexai.preview.language_models.TextGenerationModel.from_pretrained",
            return_value="Test",
        )
        model = "text-bison@001"
        project_id = "test-project"
        location = "northamerica-northeast1"
        llm = GoogleVertexAI(project_id, location, model)
        llm._validate()  # Should not raise any errors

    def test_validate_with_invalid_model(self):
        model = "invalid_model"
        project_id = "test-project"
        location = "northamerica-northeast1"
       with pytest.raises(
            UnsupportedModelError,
            match=(
                "Unsupported model: The model 'invalid-model' doesn't exist "
                "or is not supported yet."
            ),
        ):
            GoogleVertexAI(project_id, location, model)