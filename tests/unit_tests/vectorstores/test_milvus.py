import unittest
from unittest.mock import ANY, MagicMock, patch

import numpy as np  # Assuming `encode_documents` returns `numpy` arrays

from pandasai.ee.vectorstores.milvus import Milvus


class TestMilvus(unittest.TestCase):
    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_add_question_answer(self, mock_client):
        milvus = Milvus()
        milvus.add_question_answer(
            ["What is AGI?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        mock_client.return_value.insert.assert_called_once()

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_add_question_answer_with_ids(self, mock_client):
        milvus = Milvus()
        ids = ["test id 1", "test id 2"]
        documents = [
            "Q: What is AGI?\n A: print('Hello')",
            "Q: How does it work?\n A: for i in range(10): print(i)",
        ]

        # Mock the embedding function and ID conversion
        mock_ids = milvus._convert_ids(ids)

        milvus.add_question_answer(
            ["What is AGI?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
            ids=ids,
        )

        # Construct the expected data
        expected_data = [
            {"id": mock_ids[i], "vector": ANY, "document": documents[i]}
            for i in range(len(documents))
        ]

        # Assert insert was called correctly
        mock_client.return_value.insert.assert_called_once_with(
            collection_name=milvus.qa_collection_name,
            data=expected_data,
        )

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_add_question_answer_different_dimensions(self, mock_client):
        milvus = Milvus()
        with self.assertRaises(ValueError):
            milvus.add_question_answer(
                ["What is AGI?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_update_question_answer(self, mock_client):
        milvus = Milvus()
        ids = ["test id 1", "test id 2"]
        milvus.update_question_answer(
            ["test id", "test id"],
            ["What is AGI?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        mock_client.return_value.query.assert_called_once()

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_update_question_answer_different_dimensions(self, mock_client):
        milvus = Milvus()
        with self.assertRaises(ValueError):
            milvus.update_question_answer(
                ["test id"],
                ["What is AGI?", "How does it work?"],
                ["print('Hello')"],
            )

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_add_docs(self, mock_client):
        milvus = Milvus()
        milvus.add_docs(["Document 1", "Document 2"])
        mock_client.return_value.insert.assert_called_once()

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_add_docs_with_ids(self, mock_client):
        milvus = Milvus()
        ids = ["test id 1", "test id 2"]
        documents = ["Document 1", "Document 2"]

        # Mock the embedding function
        milvus.add_docs(documents, ids)

        # Assert insert was called correctly
        mock_client.return_value.insert.assert_called_once()

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_delete_question_and_answers(self, mock_client):
        milvus = Milvus()
        ids = ["id1", "id2"]
        milvus.delete_question_and_answers(ids)
        id_filter = str(milvus._convert_ids(ids))
        mock_client.return_value.delete.assert_called_once_with(
            collection_name=milvus.qa_collection_name,
            filter=f"id in {id_filter}",
        )

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_delete_docs(self, mock_client):
        milvus = Milvus()
        ids = ["id1", "id2"]
        milvus.delete_docs(ids)
        id_filter = str(milvus._convert_ids(ids))
        mock_client.return_value.delete.assert_called_once_with(
            collection_name=milvus.docs_collection_name,
            filter=f"id in {id_filter}",
        )

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_get_relevant_question_answers(self, mock_client):
        milvus = Milvus()
        question = "What is AGI?"
        mock_vector = milvus.emb_function.encode_documents(question)
        milvus.emb_function.encode_documents = MagicMock(return_value=mock_vector)

        milvus.get_relevant_question_answers(question, k=3)
        mock_client.return_value.search.assert_called_once_with(
            collection_name=milvus.qa_collection_name,
            data=mock_vector,
            limit=3,
            filter="",
            output_fields=["document"],
        )

    @patch("pandasai.ee.vectorstores.milvus.MilvusClient", autospec=True)
    def test_get_relevant_docs(self, mock_client):
        milvus = Milvus()
        question = "What is AGI?"
        mock_vector = milvus.emb_function.encode_documents(question)
        milvus.emb_function.encode_documents = MagicMock(return_value=mock_vector)

        milvus.get_relevant_docs(question, k=3)
        mock_client.return_value.search.assert_called_once_with(
            collection_name=milvus.docs_collection_name,
            data=mock_vector,
            limit=3,
            output_fields=["document"],
        )
