import unittest
from unittest.mock import patch

from pandasai.workspace import Workspace


class TestWorkspace(unittest.TestCase):
    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def setUp(self, mock_request) -> None:
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
