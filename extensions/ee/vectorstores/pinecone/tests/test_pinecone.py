import unittest
from unittest.mock import MagicMock, patch

from pandasai.helpers.logger import Logger


class TestPinecone(unittest.TestCase):
    def setUp(self):
        """Set up test-specific resources"""
        self.api_key = "test_api_key"
        # Create a mock embedding function that returns consistent embeddings
        self.mock_embedding_function = MagicMock(return_value=[[1.0, 2.0, 3.0]] * 2)

    def tearDown(self):
        """Clean up test-specific resources"""
        if hasattr(self, "vector_store"):
            self.vector_store.cleanup()
            self.vector_store = None

    @patch("pinecone.Pinecone")
    def test_constructor_with_custom_logger(self, mock_pinecone):
        """Test constructor with custom logger"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        custom_logger = Logger()
        instance = Pinecone(
            api_key=self.api_key,
            logger=custom_logger,
            embedding_function=self.mock_embedding_function,
        )
        self.assertIs(instance._logger, custom_logger)

    @patch("pinecone.Pinecone")
    def test_constructor_creates_index_if_not_exists(self, mock_pinecone):
        """Test index creation"""
        mock_instance = MagicMock()
        mock_instance.list_indexes.return_value.names.return_value = ["other_index"]
        mock_pinecone.return_value = mock_instance

        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        instance = Pinecone(
            api_key=self.api_key,
            index="test_index",
            embedding_function=self.mock_embedding_function,
        )
        self.assertIsInstance(instance._index, MagicMock)

    @patch("pinecone.Pinecone")
    def test_constructor_with_optional_parameters(self, mock_pinecone):
        """Test constructor with optional parameters"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        embedding_function = MagicMock()
        instance = Pinecone(
            api_key=self.api_key,
            embedding_function=embedding_function,
        )
        self.assertIs(instance._embedding_function, embedding_function)

    @patch("pinecone.Pinecone")
    def test_add_question_answer(self, mock_pinecone):
        """Test adding question and answer"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        self.vector_store._index = MagicMock()
        self.vector_store.add_question_answer(
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        self.vector_store._index.upsert.assert_called_once()

    @patch("pinecone.Pinecone")
    def test_add_question_answer_with_ids(self, mock_pinecone):
        """Test adding question and answer with specific IDs"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
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

    @patch("pinecone.Pinecone")
    def test_add_question_answer_different_dimensions(self, mock_pinecone):
        """Test error handling for mismatched dimensions"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        self.vector_store._index = MagicMock()
        with self.assertRaises(ValueError):
            self.vector_store.add_question_answer(
                ["What is Chroma?", "How does it work?"], ["print('Hello')"]
            )

    @patch("pinecone.Pinecone")
    def test_update_question_answer(self, mock_pinecone):
        """Test updating question and answer"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        self.vector_store._index = MagicMock()
        self.vector_store.update_question_answer(
            ["test id", "test_id 2"],
            ["What is Chroma?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        self.assertEqual(self.vector_store._index.update.call_count, 2)

    @patch("pinecone.Pinecone")
    def test_update_question_answer_different_dimensions(self, mock_pinecone):
        """Test error handling for mismatched dimensions"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        with self.assertRaises(ValueError):
            self.vector_store.update_question_answer(
                ["test id"],
                ["What is Chroma?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch("pinecone.Pinecone")
    def test_add_docs(self, mock_pinecone):
        """Test adding documents"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        self.vector_store.add_docs(["Document 1", "Document 2"])
        self.vector_store._index.upsert.assert_called_once()

    @patch("pinecone.Pinecone")
    def test_add_docs_with_ids(self, mock_pinecone):
        """Test adding documents with specific IDs"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
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

    @patch("pinecone.Pinecone")
    def test_delete_question_and_answers(self, mock_pinecone):
        """Test deleting question and answers"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        self.vector_store._index = MagicMock()
        self.vector_store.delete_question_and_answers(["id1", "id2"])
        self.vector_store._index.delete.assert_called_once_with(
            ids=["id1", "id2"], namespace="qa"
        )

    @patch("pinecone.Pinecone")
    def test_delete_docs(self, mock_pinecone):
        """Test deleting documents"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        self.vector_store._index = MagicMock()
        self.vector_store.delete_docs(["id1", "id2"])
        self.vector_store._index.delete.assert_called_once_with(
            ids=["id1", "id2"], namespace="docs"
        )

    @patch("pinecone.Pinecone")
    def test_get_relevant_question_answers(self, mock_pinecone):
        """Test getting relevant question and answers"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        self.vector_store._index.query.return_value = {
            "matches": [
                {
                    "id": "0839d1ed-9cc6-4baf-b2fa-1a084bd88a28-qa",
                    "metadata": {
                        "text": "Q: Hello World two\nA: print('hello world!')"
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
                "documents": [["Q: Hello World two\nA: print('hello world!')"]],
                "distances": [[0.350302786]],
                "metadata": [
                    [{"text": "Q: Hello World two\nA: print('hello world!')"}]
                ],
                "ids": [["0839d1ed-9cc6-4baf-b2fa-1a084bd88a28-qa"]],
            },
        )

    @patch("pinecone.Pinecone")
    def test_get_relevant_question_answers_by_ids(self, mock_pinecone):
        """Test getting relevant question and answers by IDs"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
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

    @patch("pinecone.Pinecone")
    def test_get_relevant_docs(self, mock_pinecone):
        """Test getting relevant documents"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
        self.vector_store._index.query.return_value = {
            "matches": [
                {
                    "id": "0839d1ed-9cc6-4baf-b2fa-1a084bd88a28-qa",
                    "metadata": {
                        "text": "Q: Hello World two\nA: print('hello world!')"
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
                "documents": [["Q: Hello World two\nA: print('hello world!')"]],
                "distances": [[0.350302786]],
                "metadata": [
                    [{"text": "Q: Hello World two\nA: print('hello world!')"}]
                ],
                "ids": [["0839d1ed-9cc6-4baf-b2fa-1a084bd88a28-qa"]],
            },
        )

    @patch("pinecone.Pinecone")
    def test_get_relevant_docs_by_id(self, mock_pinecone):
        """Test getting relevant documents by IDs"""
        from extensions.ee.vectorstores.pinecone.pandasai_pinecone import Pinecone

        self.vector_store = Pinecone(
            api_key=self.api_key, embedding_function=self.mock_embedding_function
        )
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


if __name__ == "__main__":
    unittest.main()
