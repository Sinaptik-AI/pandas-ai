"""Unit tests for the openai LLM class"""

import pytest

from pandasai.llm import GoogleVertexAI
from pandasai.exceptions import UnsupportedModelError


class MockedCompletion:
    def __init__(self, result: str):
        self.result = result


class TestGoogleVertexAI:
    def test_init_with_default_model(self):
        project_id = "your_project_id"
        location = "northamerica-northeast1"
        vertexai_instance = GoogleVertexAI(project_id, location)

        assert vertexai_instance.model == "text-bison@001"
        assert vertexai_instance.project_id == project_id
        assert vertexai_instance.location == location

    def test_init_with_custom_model(self):
        project_id = "test-project"
        location = "northamerica-northeast1"
        custom_model = "code-bison@001"

        vertexai_instance = GoogleVertexAI(project_id, location, model=custom_model)

        assert vertexai_instance.model == custom_model
        assert vertexai_instance.project_id == project_id
        assert vertexai_instance.location == location

    @pytest.fixture
    def google_vertexai(self):
        # Create an instance of YourClass for testing
        project_id = "test-project"
        location = "northamerica-northeast1"
        custom_model = "code-bison@001"
        return GoogleVertexAI(project_id, location, custom_model)

    def test_validate_with_model(self, google_vertexai: GoogleVertexAI):
        google_vertexai.model = "text-bison@001"
        google_vertexai._validate()  # Should not raise any errors

    def test_validate_with_invalid_model(self, google_vertexai: GoogleVertexAI):
        google_vertexai.model = "invalid-model"
        with pytest.raises(
            UnsupportedModelError,
            match=(
                "Unsupported model: The model 'invalid-model' doesn't exist "
                "or is not supported yet."
            ),
        ):
            google_vertexai._generate_text("Test prompt")

    def test_validate_without_model(self, google_vertexai: GoogleVertexAI):
        google_vertexai.model = None
        with pytest.raises(ValueError, match="model is required."):
            google_vertexai._validate()

    def test_validate_with_code_chat_model(self, google_vertexai: GoogleVertexAI):
        google_vertexai.model = "codechat-bison@001"
        google_vertexai._validate()
