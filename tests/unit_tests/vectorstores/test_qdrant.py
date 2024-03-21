import unittest
from unittest.mock import patch

from pandasai.ee.vectorstores.qdrant import Qdrant


class TestQdrant(unittest.TestCase):
    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_add_question_answer(self, mock_client):
        qdrant = Qdrant()
        qdrant.add_question_answer(
            ["What is AGI?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        mock_client.return_value.add.assert_called_once()

    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_add_question_answer_with_ids(self, mock_client):
        qdrant = Qdrant()
        ids = ["test id 1", "test id 2"]
        qdrant.add_question_answer(
            ["What is AGI?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
            ids=ids,
        )
        mock_client.return_value.add.assert_called_once_with(
            qdrant._qa_collection_name,
            documents=[
                "Q: What is AGI?\n A: print('Hello')",
                "Q: How does it work?\n A: for i in range(10): print(i)",
            ],
            metadata=None,
            ids=qdrant._convert_ids(ids),
        )

    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_add_question_answer_different_dimensions(self, mock_client):
        qdrant = Qdrant()
        with self.assertRaises(ValueError):
            qdrant.add_question_answer(
                ["What is AGI?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_update_question_answer(self, mock_client):
        qdrant = Qdrant()
        qdrant.update_question_answer(
            ["test id", "test id"],
            ["What is AGI?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        mock_client.return_value.retrieve.assert_called_once()

    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_update_question_answer_different_dimensions(self, mock_client):
        qdrant = Qdrant()
        with self.assertRaises(ValueError):
            qdrant.update_question_answer(
                ["test id"],
                ["What is AGI?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_add_docs(self, mock_client):
        qdrant = Qdrant()
        qdrant.add_docs(["Document 1", "Document 2"])
        mock_client.return_value.add.assert_called_once()

    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_add_docs_with_ids(self, mock_client):
        qdrant = Qdrant()
        ids = ["test id 1", "test id 2"]
        qdrant.add_docs(["Document 1", "Document 2"], ids)
        mock_client.return_value.add.assert_called_once_with(
            qdrant._docs_collection_name,
            documents=["Document 1", "Document 2"],
            metadata=None,
            ids=qdrant._convert_ids(ids),
        )

    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_delete_question_and_answers(self, mock_client):
        qdrant = Qdrant()
        ids = ["id1", "id2"]
        qdrant.delete_question_and_answers(ids)
        mock_client.return_value.delete.assert_called_once_with(
            qdrant._qa_collection_name,
            points_selector=qdrant._convert_ids(ids),
        )

    @patch("pandasai.ee.vectorstores.qdrant.qdrant_client.QdrantClient", autospec=True)
    def test_delete_docs(self, mock_client):
        qdrant = Qdrant()
        ids = ["id1", "id2"]
        qdrant.delete_docs(ids)
        mock_client.return_value.delete.assert_called_once_with(
            qdrant._docs_collection_name,
            points_selector=qdrant._convert_ids(ids),
        )
