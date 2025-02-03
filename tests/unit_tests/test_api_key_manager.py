import os
from unittest.mock import patch

import pytest

from pandasai.config import APIKeyManager


def test_set_api_key():
    # Setup
    test_api_key = "test-api-key-123"

    # Execute
    with patch.dict(os.environ, {}, clear=True):
        APIKeyManager.set(test_api_key)

        # Assert
        assert os.environ.get("PANDABI_API_KEY") == test_api_key
        assert APIKeyManager._api_key == test_api_key


def test_get_api_key():
    # Setup
    test_api_key = "test-api-key-123"
    APIKeyManager._api_key = test_api_key

    # Execute
    result = APIKeyManager.get()

    # Assert
    assert result == test_api_key


def test_get_api_key_when_none():
    # Setup
    APIKeyManager._api_key = None

    # Execute
    result = APIKeyManager.get()

    # Assert
    assert result is None
