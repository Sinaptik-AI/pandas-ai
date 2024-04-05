import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from pandasai.helpers.request import PandasAIApiCallError, PandasAIApiKeyError, Session


class TestSession(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["PANDASAI_API_KEY"] = "test-api-key"

    @patch("pandasai.helpers.request.requests.request")
    def test_make_request_success(self, mock_requests_request):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "mock_data"}
        mock_requests_request.return_value = mock_response

        # Create a mock Logger instance
        mock_logger = MagicMock()

        # Act
        session = Session(logger=mock_logger)
        result = session.make_request("GET", "/test_path")

        # Assert
        mock_requests_request.assert_called_with(
            "GET",
            "/api/test_path",
            headers={
                "Authorization": "Bearer test-api-key",
                "Content-Type": "application/json",
            },
            params=None,
            data=None,
            json=None,
            files=None,
            timeout=300,
        )
        self.assertEqual(result, {"data": "mock_data"})
        mock_logger.log.assert_not_called()

    @patch("pandasai.helpers.request.requests.request")
    def test_make_request_failure_status_code(self, mock_requests_request):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_requests_request.return_value = mock_response

        with self.assertRaises(PandasAIApiCallError):
            session = Session()
            session.make_request("GET", "/test_path")

    @patch("pandasai.helpers.request.requests.request")
    def test_make_request_failure_status_code_500(self, mock_requests_request):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Unauthorized"}
        mock_requests_request.return_value = mock_response

        with self.assertRaises(PandasAIApiCallError):
            session = Session()
            session.make_request("GET", "/test_path")

    @patch(
        "pandasai.helpers.request.requests.request",
        side_effect=requests.exceptions.RequestException("Mock Request Exception"),
    )
    def test_make_request_request_exception(self, mock_requests_request):
        # Arrange
        # Create a mock Logger instance
        mock_logger = MagicMock()

        # Act and Assert
        with self.assertRaises(PandasAIApiCallError):
            session = Session(logger=mock_logger)
            session.make_request("GET", "/test_path")

    def test_make_request_missing_api_key(self):
        # Arrange
        # Create a mock Logger instance
        mock_logger = MagicMock()

        # Mocking the environment variable
        with patch.dict(os.environ, {"PANDASAI_API_KEY": ""}):
            # Act and Assert
            with self.assertRaises(PandasAIApiKeyError):
                Session(logger=mock_logger)

    def test_make_request_custom_endpoint_url(self):
        # Arrange
        # Create a mock Logger instance
        mock_logger = MagicMock()

        # Act
        session = Session(endpoint_url="https://custom-api-url.com", logger=mock_logger)

        # Assert
        self.assertEqual(session._endpoint_url, "https://custom-api-url.com")
