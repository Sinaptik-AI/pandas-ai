import os
from unittest.mock import patch

import pytest

from pandasai.constants import DEFAULT_API_URL
from pandasai.exceptions import PandaAIApiKeyError
from pandasai.helpers.session import Session, get_pandaai_session


def test_session_init_without_api_key():
    """Test that Session initialization raises PandaAIApiKeyError when no API key is provided"""
    with pytest.raises(PandaAIApiKeyError) as exc_info:
        Session()
    assert (
        str(exc_info.value)
        == "PandaAI API key not found. Please set your API key using PandaAI.set_api_key() or by setting the PANDASAI_API_KEY environment variable."
    )


def test_session_init_with_none_api_key():
    """Test that Session initialization raises PandaAIApiKeyError when API key is None"""
    with pytest.raises(PandaAIApiKeyError) as exc_info:
        Session(api_key=None)
    assert (
        str(exc_info.value)
        == "PandaAI API key not found. Please set your API key using PandaAI.set_api_key() or by setting the PANDASAI_API_KEY environment variable."
    )


def test_session_init_with_api_key():
    """Test that Session initialization works with a valid API key"""
    session = Session(api_key="test-key")
    assert session._api_key == "test-key"


def test_session_init_with_default_api_url():
    """Test that Session initialization uses DEFAULT_API_URL when no URL is provided"""
    session = Session(api_key="test-key")
    assert session._endpoint_url == DEFAULT_API_URL


def test_session_init_with_custom_api_url():
    """Test that Session initialization uses provided URL"""
    custom_url = "https://custom.api.url"
    session = Session(api_key="test-key", endpoint_url=custom_url)
    assert session._endpoint_url == custom_url


@patch.dict(os.environ, {"PANDABI_API_KEY": "test-env-key"})
def test_session_init_with_env_api_key():
    """Test that Session initialization works with API key from environment"""
    session = Session()
    assert session._api_key == "test-env-key"


@patch.dict(
    os.environ,
    {"PANDABI_API_KEY": "test-env-key", "PANDABI_API_URL": "https://env.api.url"},
)
def test_session_init_with_env_api_url():
    """Test that Session initialization uses URL from environment"""
    session = Session()
    assert session._endpoint_url == "https://env.api.url"


def test_get_pandaai_session_without_credentials():
    """Test that get_pandaai_session raises PandaAIApiKeyError when no credentials are provided"""
    with pytest.raises(PandaAIApiKeyError) as exc_info:
        get_pandaai_session()
    assert (
        str(exc_info.value)
        == "PandaAI API key not found. Please set your API key using PandaAI.set_api_key() or by setting the PANDASAI_API_KEY environment variable."
    )


def test_get_pandaai_session_with_default_api_url():
    """Test that get_pandaai_session uses DEFAULT_API_URL when no URL is provided"""
    with patch.dict(os.environ, {"PANDABI_API_KEY": "test-key"}):
        session = get_pandaai_session()
        assert session._endpoint_url == DEFAULT_API_URL


@patch.dict(
    os.environ,
    {"PANDABI_API_KEY": "test-env-key", "PANDABI_API_URL": "http://test.url"},
)
def test_get_pandaai_session_with_env_credentials():
    """Test that get_pandaai_session works with credentials from environment"""
    session = get_pandaai_session()
    assert isinstance(session, Session)
    assert session._api_key == "test-env-key"
    assert session._endpoint_url == "http://test.url"


@patch.dict(
    os.environ,
    {"PANDABI_API_KEY": "test-env-key", "PANDABI_API_URL": "https://env.api.url"},
)
def test_get_pandaai_session_with_env_api_url():
    """Test that get_pandaai_session uses URL from environment"""
    session = get_pandaai_session()
    assert session._endpoint_url == "https://env.api.url"
