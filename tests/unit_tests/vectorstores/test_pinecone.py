import unittest
from unittest.mock import ANY, MagicMock, patch

from pandasai.ee.vectorstores.pinecone import Pinecone
from pandasai.helpers.logger import Logger


class TestPinecone(unittest.TestCase):
    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def setUp(self, MockPinecone):
        mock_pinecone_instance = MockPinecone.return_value
        mock_pinecone_instance.list_indexes.return_value.names.return_value = []
        mock_pinecone_instance.create_index.return_value = MagicMock()
        api_key = "test_api_key"
        self.vector_store = Pinecone(api_key=api_key)
        self.vector_store._format_qa = MagicMock(
            side_effect=lambda q, c: f"Q: {q}\nA: {c}"
        )
        self.vector_store._embedding_function = MagicMock(
            return_value=[[1.0, 2.0, 3.0]] * 2
        )
        self.vector_store._index = MagicMock()
        self.vector_store._metatext_key = "text"

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_constructor_default_parameters(self, MockPinecone):
        mock_pinecone_instance = MockPinecone.return_value
        mock_pinecone_instance.list_indexes.return_value.names.return_value = []
        mock_pinecone_instance.create_index.return_value = MagicMock()

        api_key = "test_api_key"

        instance = Pinecone(api_key=api_key)

        self.assertEqual(instance._api_key, api_key)
        self.assertEqual(instance._max_samples, 1)
        self.assertEqual(instance._similarity_threshold, 1.5)
        self.assertIsInstance(instance._logger, Logger)
        mock_pinecone_instance.create_index.assert_called_once()
        self.assertIsInstance(instance._index, MagicMock)

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_constructor_with_custom_logger(self, MockPinecone):
        mock_pinecone_instance = MockPinecone.return_value
        mock_pinecone_instance.list_indexes.return_value.names.return_value = []
        mock_pinecone_instance.create_index.return_value = MagicMock()

        api_key = "test_api_key"
        custom_logger = Logger()

        instance = Pinecone(api_key=api_key, logger=custom_logger)

        self.assertIs(instance._logger, custom_logger)

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_constructor_with_existing_index(self, MockPinecone):
        mock_pinecone_instance = MockPinecone.return_value
        mock_index = MagicMock()

        api_key = "test_api_key"

        instance = Pinecone(api_key=api_key, index=mock_index)

        self.assertIs(instance._index, mock_index)
        mock_pinecone_instance.create_index.assert_not_called()

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_constructor_creates_index_if_not_exists(self, MockPinecone):
        mock_pinecone_instance = MockPinecone.return_value
        mock_pinecone_instance.list_indexes.return_value.names.return_value = [
            "other_index"
        ]
        mock_pinecone_instance.create_index.return_value = MagicMock()

        api_key = "test_api_key"
        index_name = "pandasai"

        instance = Pinecone(api_key=api_key, index=index_name)

        mock_pinecone_instance.create_index.assert_called_once_with(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ANY,
        )
        self.assertIsInstance(instance._index, MagicMock)

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_constructor_with_optional_parameters(self, MockPinecone):
        mock_pinecone_instance = MockPinecone.return_value
        mock_pinecone_instance.list_indexes.return_value.names.return_value = []
        mock_pinecone_instance.create_index.return_value = MagicMock()

        api_key = "test_api_key"
        embedding_function = MagicMock()
        specs = MagicMock()

        instance = Pinecone(
            api_key=api_key, embedding_function=embedding_function, specs=specs
        )

        self.assertIs(instance._embedding_function, embedding_function)
        mock_pinecone_instance.create_index.assert_called_once_with(
            name="pandasai", dimension=1536, metric="cosine", spec=specs
        )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_add_question_answer(self, mock_client):
        self.vector_store._index = MagicMock()
        self.vector_store.add_question_answer(
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )

        self.vector_store._index.upsert.assert_called_once()

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_add_question_answer_with_ids(self, mock_client):
        self.vector_store._index = MagicMock()
        self.vector_store.add_question_answer(
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
            ["test id 1", "test id 2"],
        )
        self.vector_store._index.upsert.assert_called_once_with(
            vectors=[
                {
                    "id": "test id 1",
                    "values": [1.0, 2.0, 3.0],
                    "metadata": {"text": "Q: What is Chroma?\nA: print('Hello')"},
                },
                {
                    "id": "test id 2",
                    "values": [1.0, 2.0, 3.0],
                    "metadata": {
                        "text": "Q: How does it work?\nA: for i in range(10): print(i)"
                    },
                },
            ],
            namespace="qa",
        )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_add_question_answer_different_dimensions(self, mock_client):
        self.vector_store._index = MagicMock()

        with self.assertRaises(ValueError):
            self.vector_store.add_question_answer(
                ["What is Chroma?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_update_question_answer(self, mock_client):
        self.vector_store._embedding_function = MagicMock(
            return_value=[[1.0, 2.0, 3.0]] * 2
        )
        self.vector_store.update_question_answer(
            ["test id", "test_id 2"],
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )

        self.assertEqual(self.vector_store._index.update.call_count, 2)

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_update_question_answer_different_dimensions(self, mock_client):
        self.vector_store._embedding_function = MagicMock(
            return_value=[[1.0, 2.0, 3.0]]
        )
        with self.assertRaises(ValueError):
            self.vector_store.update_question_answer(
                ["test id"],
                ["What is Chroma?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_add_docs(self, mock_client):
        self.vector_store.add_docs(["Document 1", "Document 2"])
        self.vector_store._index.upsert.assert_called_once()

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_add_docs_with_ids(self, mock_client):
        self.vector_store.add_docs(
            ["Document 1", "Document 2"], ["test id 1", "test id 2"]
        )
        self.vector_store._index.upsert.assert_called_once_with(
            vectors=[
                {
                    "id": "test id 1",
                    "values": [1.0, 2.0, 3.0],
                    "metadata": {"text": "Document 1"},
                },
                {
                    "id": "test id 2",
                    "values": [1.0, 2.0, 3.0],
                    "metadata": {"text": "Document 2"},
                },
            ],
            namespace="docs",
        )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_delete_question_and_answers(self, mock_client):
        self.vector_store.delete_question_and_answers(["id1", "id2"])
        self.vector_store._index.delete.assert_called_once_with(
            ids=["id1", "id2"], namespace="qa"
        )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_delete_docs(self, mock_client):
        self.vector_store.delete_docs(["id1", "id2"])
        self.vector_store._index.delete.assert_called_once_with(
            ids=["id1", "id2"], namespace="docs"
        )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_get_relevant_question_answers(self, mock_client):
        self.vector_store._index.query.return_value = {
            "matches": [
                {
                    "id": "0839d1ed-9cc6-4baf-b2fa-1a084bd88a28-qa",
                    "metadata": {
                        "text": "Q: Hello World two\n" " A: print('hello world!')"
                    },
                    "score": 0.350302786,
                    "values": [-0.0412341766, 0.114174068, 0.024620818],
                }
            ],
            "namespace": "qa",
            "usage": {"read_units": 6},
        }
        result = self.vector_store.get_relevant_question_answers("What is Chroma?", k=3)
        self.assertEqual(
            result,
            {
                "documents": [["Q: Hello World two\n A: print('hello world!')"]],
                "distances": [[0.350302786]],
                "metadata": [
                    [{"text": "Q: Hello World two\n A: print('hello world!')"}]
                ],
                "ids": [["0839d1ed-9cc6-4baf-b2fa-1a084bd88a28-qa"]],
            },
        )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_get_relevant_question_answers_by_ids(self, mock_client):
        self.vector_store._index.fetch.return_value = {
            "documents": [["Document 1", "Document 2", "Document 3"]],
            "metadatas": [[None, None, None]],
            "ids": [["test id1", "test id2", "test id3"]],
        }
        result = self.vector_store.get_relevant_question_answers_by_id(
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

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_get_relevant_docs(self, mock_client):
        self.vector_store._index.query.return_value = {
            "matches": [
                {
                    "id": "0839d1ed-9cc6-4baf-b2fa-1a084bd88a28-qa",
                    "metadata": {
                        "text": "Q: Hello World two\n" " A: print('hello world!')"
                    },
                    "score": 0.350302786,
                    "values": [-0.0412341766, 0.114174068, 0.024620818],
                }
            ],
            "namespace": "qa",
            "usage": {"read_units": 6},
        }
        result = self.vector_store.get_relevant_docs("What is Chroma?", k=3)
        self.assertEqual(
            result,
            {
                "documents": [["Q: Hello World two\n A: print('hello world!')"]],
                "distances": [[0.350302786]],
                "metadata": [
                    [{"text": "Q: Hello World two\n A: print('hello world!')"}]
                ],
                "ids": [["0839d1ed-9cc6-4baf-b2fa-1a084bd88a28-qa"]],
            },
        )

    @patch("pandasai.ee.vectorstores.pinecone.pinecone.Pinecone", autospec=True)
    def test_get_relevant_docs_by_id(self, mock_client):
        self.vector_store._index.fetch.return_value = {
            "documents": [["Document 1", "Document 2", "Document 3"]],
            "metadatas": [[None, None, None]],
            "ids": [["test id1", "test id2", "test id3"]],
        }
        result = self.vector_store.get_relevant_docs_by_id(
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
