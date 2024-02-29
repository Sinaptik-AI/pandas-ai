import unittest
from unittest.mock import patch

from pandasai.vectorstores.bamboo_vectorstore import BambooVectorStore


class TestBambooVector(unittest.TestCase):
    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_add_question_answer(self, mock_request):
        bvs = BambooVectorStore(api_key="dummy_key")
        bvs.add_question_answer(
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        call_args = mock_request.call_args_list[0][0]
        mock_request.assert_called_once()
        assert call_args[1] == "POST"
        assert call_args[2] == "/training-data"
        assert mock_request.call_args_list[0][1] == {
            "json": {
                "code": ["print('Hello')", "for i in range(10): print(i)"],
                "query": ["What is Chroma?", "How does it work?"],
            }
        }

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_add_docs(self, mock_request):
        bvs = BambooVectorStore(api_key="dummy_key")
        bvs.add_docs(["What is Chroma?"])
        call_args = mock_request.call_args_list[0][0]
        mock_request.assert_called_once()
        assert call_args[1] == "POST"
        assert call_args[2] == "/training-docs"
        assert mock_request.call_args_list[0][1] == {
            "json": {"docs": ["What is Chroma?"]}
        }

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_get_qa(self, mock_request):
        bvs = BambooVectorStore(api_key="dummy_key")
        bvs.get_relevant_qa_documents("Chroma")
        mock_request.assert_called_once()

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_get_qa_args(self, mock_request):
        bvs = BambooVectorStore(api_key="dummy_key")
        bvs.get_relevant_qa_documents("Chroma")
        call_args = mock_request.call_args_list[0][0]
        mock_request.assert_called_once()
        assert call_args[1] == "GET"
        assert call_args[2] == "/training-data/qa/relevant-qa"
        assert mock_request.call_args_list[0][1] == {
            "params": {"count": 1, "query": "Chroma"}
        }

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_get_docs(self, mock_request):
        bvs = BambooVectorStore(api_key="dummy_key")
        bvs.get_relevant_docs_documents("Chroma")
        mock_request.assert_called_once()

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_get_docs_args(self, mock_request):
        bvs = BambooVectorStore(api_key="dummy_key")
        bvs.get_relevant_docs_documents("Chroma")
        call_args = mock_request.call_args_list[0][0]
        mock_request.assert_called_once()
        assert call_args[1] == "GET"
        assert call_args[2] == "/training-docs/docs/relevant-docs"
        assert mock_request.call_args_list[0][1] == {
            "params": {"count": 3, "query": "Chroma"}
        }
