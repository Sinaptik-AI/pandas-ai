import os
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from pandasai.exceptions import PandasAIDatasetUploadFailed
from pandasai.workspace import Workspace


class TestWorkspace(unittest.TestCase):
    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def setUp(self, mock_request) -> None:
        os.environ["PANDASAI_API_KEY"] = "test-api-key"
        self.workspace = Workspace("workspace2")

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_constructor(self, mock_request):
        Workspace("workspace1")
        call_args = mock_request.call_args_list[0][0]
        mock_request.assert_called_once()
        assert call_args[1] == "POST"
        assert call_args[2] == "/spaces/initialize"
        assert mock_request.call_args_list[0][1] == {"json": {"slug": "workspace1"}}

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_chat_method(self, mock_request):
        self.workspace.chat("query1")
        call_args = mock_request.call_args_list[0][0]
        assert call_args[1] == "POST"
        assert call_args[2] == "/chat"
        json_data = mock_request.call_args_list[0][1]
        assert json_data["json"]["query"] == "query1"

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_chat_method_calling_two_time_conv_id_exists(self, mock_request):
        self.workspace.chat("query1")
        self.workspace.chat("query2")
        call_args = mock_request.call_args_list[1][0]
        assert call_args[1] == "POST"
        assert call_args[2] == "/chat"
        json_data = mock_request.call_args_list[1][1]
        assert json_data["json"]["query"] == "query2"

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_chat_method_check_space_id_passed(self, mock_request):
        mock_request.return_value = {
            "data": {
                "id": "12345",
                "conversation_id": "12345",
                "response": [{"type": "string", "value": "hello world!"}],
            }
        }
        workspace = Workspace("workspace2")
        workspace.chat("query1")
        call_args = mock_request.call_args_list[1][0]
        assert call_args[1] == "POST"
        assert call_args[2] == "/chat"
        json_data = mock_request.call_args_list[1][1]
        assert json_data["json"]["query"] == "query1"
        assert json_data["json"]["space_id"] == "12345"

    @patch("pandasai.workspace.requests.post")
    @patch("pandasai.helpers.request.Session.post")
    def test_push_success(self, mock_session_post, mock_requests_post):
        # Arrange
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        name = "test_dataset"
        description = "Test dataset description"

        # Mock responses
        mock_session_post.side_effect = [
            {"data": {"id": "1"}},
            {
                "data": {
                    "upload_url": {
                        "url": "mock_upload_url",
                        "fields": {"key1": "value1"},
                    },
                    "id": "1",
                }
            },
            {"data": {"id": "mock_data_id"}},
        ]
        mock_requests_post.return_value.status_code = 204

        # Create a mock Session instance
        mock_session = MagicMock()
        mock_session.post.return_value = {
            "data": {
                "upload_url": {"url": "mock_upload_url", "fields": {"key1": "value1"}}
            }
        }

        workspace = Workspace("test-space")
        workspace.push(df, name, description)

        assert mock_session_post.call_args_list[1][0][0] == "/table"
        assert mock_session_post.call_args_list[1][1] == {
            "json": {"name": name, "description": description}
        }

        mock_requests_post.assert_called_with(
            "mock_upload_url",
            data={"key1": "value1"},
            files={"file": df.to_csv(index=False).encode("utf-8")},
        )

        print(mock_session_post.call_args_list[2])
        assert mock_session_post.call_args_list[2][0][0] == "/table/file-uploaded"
        assert mock_session_post.call_args_list[2][1] == {
            "json": {"space_id": workspace._id, "dataframe_id": "1"}
        }

    @patch("pandasai.workspace.requests.post")
    @patch("pandasai.helpers.request.Session.post")
    def test_push_upload_exception(self, mock_session_post, mock_requests_post):
        # Arrange
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        name = "test_dataset"
        description = "Test dataset description"

        # Mock responses
        mock_session_post.side_effect = [
            {"data": {"id": "1"}},
            {
                "data": {
                    "upload_url": {
                        "url": "mock_upload_url",
                        "fields": {"key1": "value1"},
                    },
                    "id": "1",
                }
            },
            {"data": {"id": "mock_data_id"}},
        ]
        mock_requests_post.return_value.status_code = 400

        # Create a mock Session instance
        mock_session = MagicMock()
        mock_session.post.return_value = {
            "data": {
                "upload_url": {"url": "mock_upload_url", "fields": {"key1": "value1"}}
            }
        }

        workspace = Workspace("test-space")

        with self.assertRaises(PandasAIDatasetUploadFailed):
            workspace.push(df, name, description)
