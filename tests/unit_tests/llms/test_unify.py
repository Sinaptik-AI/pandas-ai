import pytest
from unittest.mock import patch, MagicMock
from pandasai.llm import Unify
from pandasai.exceptions import APIKeyNotFoundError

# Mock the unify.clients module
unify_clients_mock = MagicMock()

@pytest.fixture
def mock_unify_client():
    with patch('unify.clients.Unify') as mock:
        yield mock

@pytest.fixture
def mock_env_variables(monkeypatch):
    monkeypatch.setenv("UNIFY_KEY", "test_api_key")

def test_unify_initialization(mock_unify_client, mock_env_variables):
    unify = Unify(model="test_model", provider="test_provider")
    assert unify.api_key == "test_api_key"
    assert unify.model == "test_model"
    assert unify.provider == "test_provider"
    mock_unify_client.assert_called_once_with(
        api_key="test_api_key",
        endpoint=None,
        model="test_model",
        provider="test_provider"
    )

def test_unify_initialization_with_endpoint(mock_unify_client, mock_env_variables):
    unify = Unify(endpoint="test_model@test_provider")
    assert unify.api_key == "test_api_key"
    assert unify.model == "test_model"
    assert unify.provider == "test_provider"
    mock_unify_client.assert_called_once_with(
        api_key="test_api_key",
        endpoint="test_model@test_provider",
        model="test_model",
        provider="test_provider"
    )

def test_unify_initialization_without_api_key():
    with pytest.raises(APIKeyNotFoundError):
        Unify(model="test_model", provider="test_provider")

def test_unify_initialization_with_additional_params(mock_unify_client, mock_env_variables):
    unify = Unify(model="test_model", provider="test_provider", max_tokens=100, temperature=0.7)
    mock_unify_client.assert_called_once_with(
        api_key="test_api_key",
        endpoint=None,
        model="test_model",
        provider="test_provider",
        max_tokens=100,
        temperature=0.7
    )

def test_unify_chat_completion(mock_unify_client, mock_env_variables):
    mock_generate = MagicMock(return_value="Test response")
    mock_unify_client.return_value.generate = mock_generate

    unify = Unify(model="test_model", provider="test_provider")
    response = unify.chat_completion("Test prompt")

    assert response == {"choices": [{"message": {"content": "Test response"}}]}
    mock_generate.assert_called_once_with(
        user_prompt="Test prompt",
        max_tokens=1024,
        temperature=1.0,
        stop=None
    )

def test_unify_call(mock_unify_client, mock_env_variables):
    mock_generate = MagicMock(return_value="Test response")
    mock_unify_client.return_value.generate = mock_generate

    unify = Unify(model="test_model", provider="test_provider")
    response = unify.call("Test instruction", "Test value", "Test suffix")

    assert response == "Test response"
    mock_generate.assert_called_once_with(
        user_prompt="Test instruction\n\nTest value\n\nTest suffix",
        max_tokens=1024,
        temperature=1.0,
        stop=None
    )

def test_unify_type():
    unify = Unify(model="test_model", provider="test_provider", api_token="test_token")
    assert unify.type == "unify"