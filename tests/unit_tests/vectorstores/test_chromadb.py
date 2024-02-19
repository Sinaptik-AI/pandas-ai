import unittest
from unittest.mock import patch
from pandasai.vectorstores.chroma import Chroma


class TestChroma(unittest.TestCase):
    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_add_question_answer(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        chroma = Chroma()
        chroma.add_question_answer(
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        mock_collection.add.assert_called_once()

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_add_question_answer_with_ids(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        chroma = Chroma()
        chroma.add_question_answer(
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
            ["test id 1", "test id 2"],
        )
        mock_collection.add.assert_called_once_with(
            documents=[
                "Q: What is Chroma?\n A: print('Hello')",
                "Q: How does it work?\n A: for i in range(10): print(i)",
            ],
            metadatas=None,
            ids=["test id 1", "test id 2"],
        )

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_add_question_answer_different_dimensions(
        self, mock_client, mock_collection
    ):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        chroma = Chroma()
        with self.assertRaises(ValueError):
            chroma.add_question_answer(
                ["What is Chroma?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_update_question_answer(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        chroma = Chroma()
        chroma.update_question_answer(
            ["test id"],
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        mock_collection.update.assert_called_once()

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_update_question_answer_different_dimensions(
        self, mock_client, mock_collection
    ):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        chroma = Chroma()
        with self.assertRaises(ValueError):
            chroma.update_question_answer(
                ["test id"],
                ["What is Chroma?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_add_docs(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma.add_docs(["Document 1", "Document 2"])
        mock_collection.add.assert_called_once()

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_add_docs_with_ids(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma.add_docs(["Document 1", "Document 2"], ["test id 1", "test id 2"])
        mock_collection.add.assert_called_once_with(
            documents=["Document 1", "Document 2"],
            metadatas=None,
            ids=["test id 1", "test id 2"],
        )

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_delete_question_and_answers(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma._qa_collection = mock_collection
        chroma.delete_question_and_answers(["id1", "id2"])
        mock_collection.delete.assert_called_once_with(ids=["id1", "id2"])

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_delete_docs(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma._docs_collection = mock_collection
        chroma.delete_docs(["id1", "id2"])
        mock_collection.delete.assert_called_once_with(ids=["id1", "id2"])

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_get_relevant_question_answers(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma._qa_collection = mock_collection
        mock_collection.query.return_value = {
            "documents": [["Document 1", "Document 2", "Document 3"]],
            "distances": [[0.5, 0.8, 1.0]],
            "metadatas": [[None, None, None]],
            "ids": [["test id1", "test id2", "test id3"]],
        }
        result = chroma.get_relevant_question_answers("What is Chroma?", k=3)
        self.assertEqual(
            result,
            {
                "documents": [["Document 1", "Document 2", "Document 3"]],
                "distances": [[0.5, 0.8, 1.0]],
                "metadatas": [[None, None, None]],
                "ids": [["test id1", "test id2", "test id3"]],
            },
        )

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_get_relevant_question_answers_by_ids(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma._qa_collection = mock_collection
        mock_collection.get.return_value = {
            "documents": [["Document 1", "Document 2", "Document 3"]],
            "metadatas": [[None, None, None]],
            "ids": [["test id1", "test id2", "test id3"]],
        }
        result = chroma.get_relevant_question_answers_by_id(
            ["test id1", "test id2", "test id3"]
        )
        self.assertEqual(
            result,
            {
                "documents": [["Document 1", "Document 2", "Document 3"]],
                "metadatas": [[None, None, None]],
                "ids": [["test id1", "test id2", "test id3"]],
            },
        )

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_get_relevant_docs(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma._docs_collection = mock_collection
        mock_collection.query.return_value = {
            "documents": [["Document 1", "Document 2", "Document 3"]],
            "distances": [[0.5, 0.8, 1.0]],
            "metadatas": [[None, None, None]],
            "ids": [["test id1", "test id2", "test id3"]],
        }
        result = chroma.get_relevant_docs("What is Chroma?", k=3)
        self.assertEqual(
            result,
            {
                "documents": [["Document 1", "Document 2", "Document 3"]],
                "distances": [[0.5, 0.8, 1.0]],
                "metadatas": [[None, None, None]],
                "ids": [["test id1", "test id2", "test id3"]],
            },
        )

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_get_relevant_docs_by_id(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma._docs_collection = mock_collection
        mock_collection.get.return_value = {
            "documents": [["Document 1", "Document 2", "Document 3"]],
            "metadatas": [[None, None, None]],
            "ids": [["test id1", "test id2", "test id3"]],
        }
        result = chroma.get_relevant_docs_by_id(["test id1", "test id2", "test id3"])
        self.assertEqual(
            result,
            {
                "documents": [["Document 1", "Document 2", "Document 3"]],
                "metadatas": [[None, None, None]],
                "ids": [["test id1", "test id2", "test id3"]],
            },
        )

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_get_relevant_question_answers_documents(
        self, mock_client, mock_collection
    ):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma._qa_collection = mock_collection
        mock_collection.query.return_value = {
            "documents": [["Document 1", "Document 2", "Document 3"]],
            "distances": [[0.5, 0.8, 1.0]],
            "metadatas": [[None, None, None]],
            "ids": [["test id1", "test id2", "test id3"]],
        }
        result = chroma.get_relevant_qa_documents("What is Chroma?", k=3)
        self.assertEqual(result, ["Document 1", "Document 2", "Document 3"])

    @patch(
        "pandasai.vectorstores.chroma.chromadb.api.models.Collection.Collection",
        autospec=True,
    )
    @patch("pandasai.vectorstores.chroma.chromadb.Client", autospec=True)
    def test_get_relevant_docs_documents(self, mock_client, mock_collection):
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        chroma = Chroma()
        chroma._qa_collection = mock_collection
        mock_collection.query.return_value = {
            "documents": [["Document 1", "Document 2", "Document 3"]],
            "distances": [[0.5, 0.8, 1.0]],
            "metadatas": [[None, None, None]],
            "ids": [["test id1", "test id2", "test id3"]],
        }
        result = chroma.get_relevant_docs_documents("What is Chroma?", k=3)
        self.assertEqual(result, ["Document 1", "Document 2", "Document 3"])
