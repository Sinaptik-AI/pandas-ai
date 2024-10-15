import os
import shutil
import unittest
from unittest.mock import MagicMock

from extensions.ee.lancedb.lancedb import LanceDB
from pandasai.helpers.logger import Logger


class TestLanceDB(unittest.TestCase):
    def setUp(self):
        # Mock the LanceDB class within the setUp method
        self.vector_store = LanceDB()
        self.vector_store._format_qa = MagicMock(
            side_effect=lambda q, c: f"Q: {q}\nA: {c}"
        )

    def tearDown(self) -> None:
        path = "/tmp/lancedb"
        if os.path.exists(path):
            shutil.rmtree(path)

    def test_constructor_default_parameters(self):
        self.assertEqual(self.vector_store._max_samples, 1)
        self.assertEqual(self.vector_store._similarity_threshold, 1.5)
        self.assertIsInstance(self.vector_store._logger, Logger)
        assert "pandasai-qa" in self.vector_store._db.table_names()
        assert "pandasai-docs" in self.vector_store._db.table_names()

    def test_constructor_with_custom_logger(self):
        custom_logger = Logger()
        self.vector_store._logger = custom_logger
        self.assertIs(self.vector_store._logger, custom_logger)

    def test_constructor_creates_table_if_not_exists(self):
        index_name = "pandasai"
        exists = f"{index_name}-qa" in self.vector_store._db.table_names()
        self.assertEqual(exists, True)

    def test_add_question_answer(self):
        inserted_ids = self.vector_store.add_question_answer(
            ["What is LanceDB?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
        )
        assert len(inserted_ids) == 2

    def test_add_question_answer_with_ids(self):
        inserted_ids = self.vector_store.add_question_answer(
            ["What is LanceDB?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
            ["test_id_11", "test_id_12"],
        )
        assert inserted_ids == ["test_id_11", "test_id_12"]

    def test_add_question_answer_different_dimensions(self):
        with self.assertRaises(ValueError):
            self.vector_store.add_question_answer(
                ["What is LanceDB?", "How does it work?"],
                ["print('Hello')"],
            )

    def test_update_question_answer(self):
        updated_ids = self.vector_store.update_question_answer(
            ["test_id"],
            ["What is LanceDB?"],
            ["print(Hello)"],
        )
        self.assertEqual(updated_ids, ["test_id"])

    def test_update_question_answer_different_dimensions(self):
        with self.assertRaises(ValueError):
            self.vector_store.update_question_answer(
                ["test_id"],
                ["What is LanceDB?", "How does it work?"],
                ["print('Hello')"],
            )

    def test_add_docs(self):
        inserted_ids = self.vector_store.add_docs(["Document 1", "Document 2"])
        self.assertEqual(len(inserted_ids), 2)

    def test_add_docs_with_ids(self):
        inserted_ids = self.vector_store.add_docs(
            ["Document 1", "Document 2"], ["test_id_1", "test_id_2"]
        )
        self.assertEqual(inserted_ids, ["test_id_1", "test_id_2"])

    def test_delete_question_and_answers(self):
        deleted_qa = self.vector_store.delete_question_and_answers(["id1", "id2"])
        self.assertEqual(deleted_qa, True)

    def test_delete_docs(self):
        deleted_docs = self.vector_store.delete_docs(["id1", "id2"])
        self.assertEqual(deleted_docs, True)

    def test_get_relevant_question_answers(self):
        self.vector_store.add_question_answer(
            ["What is LanceDB?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
            ["test_id_11", "test_id_12"],
        )
        result = self.vector_store.get_relevant_question_answers(
            "What is LanceDB?", k=2
        )

        self.assertEqual(
            result,
            {
                "documents": [
                    [
                        "Q: What is LanceDB?\nA: print('Hello')",
                        "Q: How does it work?\nA: for i in range(10): print(i)",
                    ]
                ],
                "metadatas": [["None", "None"]],
            },
        )

    def test_get_relevant_question_answers_by_ids(self):
        self.vector_store.add_question_answer(
            ["What is LanceDB?", "How does it work?"],
            ["print('Hello')", "for i in range(10): print(i)"],
            ["test_id_11", "test_id_12"],
        )
        result = self.vector_store.get_relevant_question_answers_by_id(["test_id_11"])
        print(result)
        self.assertEqual(
            result,
            [
                [
                    {
                        "metadata": "None",
                        "qa": "Q: What is LanceDB?\nA: print('Hello')",
                    }
                ]
            ],
        )

    def test_get_relevant_docs(self):
        self.vector_store.add_docs(
            ["Document 1", "Document 2", "Document 3"],
            ["test_id_1", "test_id_2", "test_id_3"],
        )
        result = self.vector_store.get_relevant_docs("What is LanceDB?", k=3)
        self.assertEqual(
            result,
            {
                "documents": [["Document 1", "Document 2", "Document 3"]],
                "metadatas": [["None", "None", "None"]],
            },
        )

    def test_get_relevant_docs_by_ids(self):
        self.vector_store.add_docs(
            ["Document 1", "Document 2", "Document 3"],
            ["test_id_1", "test_id_2", "test_id_3"],
        )
        result = self.vector_store.get_relevant_docs_by_id(["test_id_1"])
        self.assertEqual(result, [[{"doc": "Document 1", "metadata": "None"}]])


if __name__ == "__main__":
    unittest.main()
