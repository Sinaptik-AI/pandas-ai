from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(scope="session")
def mock_json_load():
    mock = MagicMock()

    with patch("json.load", mock):
        yield mock
