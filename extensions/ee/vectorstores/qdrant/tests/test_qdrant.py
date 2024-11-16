import unittest
import uuid
from unittest.mock import patch, MagicMock

from qdrant_client import models

from extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant import (
    Qdrant,
    UUID_NAMESPACE,
)


class TestQdrant(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.set_model = MagicMock()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_add_question_answer(self, mock_client):
        mock_client.return_value = self.mock_client
        qdrant = Qdrant()
        qdrant.add_question_answer(
            ["What is AGI?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        mock_client.return_value.upsert.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_add_question_answer_with_ids(self, mock_client):
        mock_client.return_value = self.mock_client
        qdrant = Qdrant()
        ids = ["test id 1", "test id 2"]
        qdrant.add_question_answer(
            ["What is AGI?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
            ids=ids,
        )
        mock_client.return_value.upsert.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_update_question_answer(self, mock_client):
        mock_client.return_value = self.mock_client
        test_id = str(uuid.uuid5(uuid.UUID(UUID_NAMESPACE), "test_id"))
        mock_client.return_value.retrieve.return_value = [
            models.Record(id=test_id, payload={})
        ]
        qdrant = Qdrant()
        qdrant.update_question_answer(
            ["test_id"],
            ["What is AGI?"],
            ["print('Hello')"],
        )
        mock_client.return_value.upsert.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_add_docs(self, mock_client):
        mock_client.return_value = self.mock_client
        qdrant = Qdrant()
        qdrant.add_docs(["Document 1", "Document 2"])
        mock_client.return_value.upsert.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_add_docs_with_ids(self, mock_client):
        mock_client.return_value = self.mock_client
        qdrant = Qdrant()
        ids = ["test id 1", "test id 2"]
        qdrant.add_docs(["Document 1", "Document 2"], ids=ids)
        mock_client.return_value.upsert.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_delete_question_and_answers(self, mock_client):
        mock_client.return_value = self.mock_client
        qdrant = Qdrant()
        ids = ["test id 1", "test id 2"]
        qdrant.delete_question_and_answers(ids)
        mock_client.return_value.delete.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_delete_docs(self, mock_client):
        mock_client.return_value = self.mock_client
        qdrant = Qdrant()
        ids = ["test id 1", "test id 2"]
        qdrant.delete_docs(ids)
        mock_client.return_value.delete.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_get_relevant_question_answers(self, mock_client):
        mock_client.return_value = self.mock_client
        mock_client.return_value.search.return_value = [
            models.ScoredPoint(
                id="test_id",
                version=1,
                score=0.9,
                payload={"document": "test document", "metadata": {}},
                vector=None,
            )
        ]
        qdrant = Qdrant()
        result = qdrant.get_relevant_question_answers("test question")
        self.assertEqual(result["documents"], ["test document"])
        mock_client.return_value.search.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_get_relevant_question_answers_by_ids(self, mock_client):
        mock_client.return_value = self.mock_client
        mock_client.return_value.retrieve.return_value = [
            models.Record(
                id="test_id",
                payload={"document": "test document", "metadata": {}},
            )
        ]
        qdrant = Qdrant()
        result = qdrant.get_relevant_question_answers_by_id(["test_id"])
        self.assertEqual(result["documents"], ["test document"])
        mock_client.return_value.retrieve.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_get_relevant_docs(self, mock_client):
        mock_client.return_value = self.mock_client
        mock_client.return_value.search.return_value = [
            models.ScoredPoint(
                id="test_id",
                version=1,
                score=0.9,
                payload={"document": "test document", "metadata": {}},
                vector=None,
            )
        ]
        qdrant = Qdrant()
        result = qdrant.get_relevant_docs("test question")
        self.assertEqual(result["documents"], ["test document"])
        mock_client.return_value.search.assert_called_once()

    @patch(
        "extensions.ee.vectorstores.qdrant.pandasai_qdrant.qdrant.qdrant_client.QdrantClient",
        autospec=True,
    )
    def test_get_relevant_docs_by_id(self, mock_client):
        mock_client.return_value = self.mock_client
        mock_client.return_value.retrieve.return_value = [
            models.Record(
                id="test_id",
                payload={"document": "test document", "metadata": {}},
            )
        ]
        qdrant = Qdrant()
        result = qdrant.get_relevant_docs_by_id(["test_id"])
        self.assertEqual(result["documents"], ["test document"])
        mock_client.return_value.retrieve.assert_called_once()
