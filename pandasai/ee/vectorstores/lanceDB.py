import uuid
from typing import Callable, Iterable, List, Optional, Union

import lancedb
import pandas as pd
from lancedb.embeddings import EmbeddingFunctionRegistry, get_registry
from lancedb.embeddings.base import TextEmbeddingFunction
from lancedb.embeddings.registry import register
from lancedb.pydantic import LanceModel, Vector
from sentence_transformers import SentenceTransformer

from pandasai.helpers.logger import Logger
from pandasai.vectorstores.vectorstore import VectorStore


@register("embedding_function")
class EmbeddingFunction(TextEmbeddingFunction):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self._ndims = None
        self._model = model

    def generate_embeddings(self, texts):
        return self._model(list(texts))

    def ndims(self):
        if self._ndims is None:
            self._ndims = len(self.generate_embeddings(texts=["foo"])[0])
        return self._ndims


class Schema:
    def __init__(self, custom_embedding_function, model=None):
        if custom_embedding_function:
            self._embed = (
                EmbeddingFunctionRegistry.get_instance(model)
                .get("embedding_function")
                .create()
            )
        else:
            self._embed = (
                get_registry()
                .get("sentence-transformers")
                .create(name="BAAI/bge-small-en-v1.5", device="cpu")
            )

    def _create_schema(self):
        class QA_pairs(LanceModel):
            id: str
            qa: str = self._embed.SourceField()
            metadata: str
            vector: Vector(self._embed.ndims()) = self._embed.VectorField()

        # schema for docs
        class Docs(LanceModel):
            id: str
            doc: str = self._embed.SourceField()
            metadata: str
            vector: Vector(self._embed.ndims()) = self._embed.VectorField()

        return QA_pairs, Docs


class LanceDB(VectorStore):
    """
    Implementation of LanceDB vector store
    """

    _logger: Logger

    def __init__(
        self,
        table_name: str = "pandasai",
        embedding_function: Optional[Callable[[List[str]], List[float]]] = None,
        persist_path: Optional[str] = "/tmp/lancedb",
        max_samples: int = 1,
        similary_threshold: int = 1.5,
        logger: Optional[Logger] = None,
    ) -> None:
        self._logger = logger or Logger()
        self._max_samples = max_samples
        self._similarity_threshold = similary_threshold
        self._persist_directory = persist_path

        # Initialize LanceDB database
        self._db = lancedb.connect(self._persist_directory)

        # Embedding function
        self._embedding_function = embedding_function
        if self._embedding_function is None:
            QA_pairs, Docs = Schema(custom_embedding_function=False)._create_schema()
        else:
            QA_pairs, Docs = Schema(
                custom_embedding_function=True, model=self._embedding_function
            )._create_schema()

        self._logger.log(f"Persisting Agent Training data in {self._persist_directory}")

        # table for qa pairs
        if f"{table_name}-qa" not in self._db.table_names():
            self._qa_table = self._db.create_table(f"{table_name}-qa", schema=QA_pairs)
        else:
            self._qa_table = self._db.open_table(f"{table_name}-qa")

        # table for docs
        if f"{table_name}-docs" not in self._db.table_names():
            self._docs_table = self._db.create_table(f"{table_name}-docs", schema=Docs)
        else:
            self._docs_table = self._db.open_table(f"{table_name}-docs")

        self._logger.log(f"Successfully initialized collection {table_name}")

    def add_question_answer(
        self,
        queries: Iterable[str],
        codes: Iterable[str],
        ids: Optional[Iterable[str]] = None,
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Add question and answer(code) to the training set
        Args:
            query: string of question
            code: str
            ids: Optional Iterable of ids associated with the texts.
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters
        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        if len(queries) != len(codes):
            raise ValueError(
                f"Queries and codes dimension doesn't match {len(queries)} != {len(codes)}"
            )

        if ids is None:
            ids = [f"{str(uuid.uuid4())}-qa" for _ in queries]
        qa_str = [self._format_qa(query, code) for query, code in zip(queries, codes)]

        if metadatas is not None and len(metadatas):
            metadatas = [str(data) for data in metadatas]
        else:
            metadatas = ["None" for _ in range(len(ids))]

        if self._embedding_function is not None:
            embeddings = self._embedding_function(qa_str)
            data = {
                "id": ids,
                "qa": qa_str,
                "metadata": metadatas,
                "vector": embeddings,
            }
        else:
            data = {"id": ids, "qa": qa_str, "metadata": metadatas}

        df = pd.DataFrame(data)
        self._qa_table.add(df)

        return ids

    def add_docs(
        self,
        docs: Iterable[str],
        ids: Optional[Iterable[str]] = None,
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Add docs to the training set
        Args:
            docs: Iterable of strings to add to the vectorstore.
            ids: Optional Iterable of ids associated with the texts.
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        if ids is None:
            ids = [f"{str(uuid.uuid4())}-docs" for _ in docs]

        if metadatas is not None and len(metadatas):
            metadatas = [str(data) for data in metadatas]
        else:
            metadatas = ["None" for _ in range(len(ids))]

        if self._embedding_function is not None:
            embeddings = self._embedding_function(docs)
            data = {
                "id": ids,
                "doc": docs,
                "metadata": metadatas,
                "vector": embeddings,
            }
        else:
            data = {"id": ids, "doc": docs, "metadata": metadatas}

        df = pd.DataFrame(data)
        self._docs_table.add(df)

        return ids

    def get_embeddings(self, text):
        if self._embedding_function is not None:
            return self._embedding_function([text])

        model = SentenceTransformer("BAAI/bge-large-zh-v1.5")
        embedding_function = model.encode(text, normalize_embeddings=True)
        return embedding_function(text)

    def update_question_answer(
        self,
        ids: Iterable[str],
        queries: Iterable[str],
        codes: Iterable[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Update question and answer(code) to the training set
        Args:
            ids: Iterable of ids associated with the texts.
            queries: string of question
            codes: str
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters
        Returns:
            List of ids from updating the texts into the vectorstore.
        """
        if len(queries) != len(codes):
            raise ValueError(
                f"Queries and codes dimension doesn't match {len(queries)} != {len(codes)}"
            )

        qa_str = [self._format_qa(query, code) for query, code in zip(queries, codes)]
        if metadatas is not None and len(metadatas):
            metadatas = [str(data) for data in metadatas]
        else:
            metadatas = ["None" for _ in range(len(ids))]

        for i in range(len(ids)):
            updated_values = {
                "qa": str(qa_str[i]),
                "metadata": metadatas[i],
            }
            self._qa_table.update(values=updated_values, where=f"id = '{ids[i]}'")

        return ids

    def update_docs(
        self,
        ids: Iterable[str],
        docs: Iterable[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Update docs to the training set
        Args:
            ids: Iterable of ids associated with the texts.
            docs: Iterable of strings to update to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        if metadatas is not None and len(metadatas):
            metadatas = [str(data) for data in metadatas]
        else:
            metadatas = ["None" for _ in range(len(ids))]

        for i in range(len(ids)):
            updated_values = {
                "doc": str(docs[i]),
                "metadata": metadatas[i],
            }
            self._docs_table.update(values=updated_values, where=f"id = '{ids[i]}'")
        return ids

    def delete_question_and_answers(
        self, ids: Optional[List[str]] = None
    ) -> Optional[bool]:
        """
        Delete by vector ID to delete question and answers
        Args:
            ids: List of ids to delete

        Returns:
            Optional[bool]: True if deletion is successful,
            False otherwise
        """
        for id in ids:
            self._qa_table.delete(f"id = '{id}'")
        return True

    def delete_docs(self, ids: Optional[List[str]] = None) -> Optional[bool]:
        """
        Delete by vector ID to delete docs
        Args:
            ids: List of ids to delete

        Returns:
            Optional[bool]: True if deletion is successful,
            False otherwise
        """
        for id in ids:
            self._docs_table.delete(f"id = '{id}'")
        return True

    def get_relevant_question_answers(
        self, question: str, k: Union[int, None] = None
    ) -> List[dict]:
        """
        Returns relevant question answers based on search
        """
        k = k or self._max_samples

        if self._embedding_function is None:
            relevant_data = self._qa_table.search(query=question).limit(k).to_list()
        else:
            question_embeddings = self._embedding_function([question])
            relevant_data = (
                self._qa_table.search(question_embeddings).limit(k).to_list()
            )

        return self._filter_docs_based_on_distance(
            relevant_data, self._similarity_threshold
        )

    def get_relevant_docs(self, question: str, k: int = None) -> List[dict]:
        """
        Returns relevant documents based search
        """
        k = k or self._max_samples

        if self._embedding_function is None:
            relevant_data = self._docs_table.search(query=question).limit(k).to_list()
        else:
            question_embeddings = self._embedding_function([question])
            relevant_data = (
                self._docs_table.search(question_embeddings).limit(k).to_list()
            )

        return self._filter_docs_based_on_distance(
            relevant_data, self._similarity_threshold
        )

    def get_relevant_question_answers_by_id(self, ids: Iterable[str]) -> List[dict]:
        """
        Returns relevant question answers based on ids
        """
        # to_search = ', ' .join([str(id) for id in ids])
        results = []
        for qa_id in ids:
            relevant_data = (
                self._qa_table.search()
                .limit(len(self._qa_table))
                .where(f"id = '{qa_id}'")
                .select(["metadata", "qa"])
                .to_list()
            )
            results.append(relevant_data)
        return results

    def get_relevant_docs_by_id(self, ids: Iterable[str]) -> List[dict]:
        """
        Returns relevant question answers based on ids
        """
        # to_search = ', '.join([str(id) for id in ids])
        results = []
        for doc_id in ids:
            relevant_data = (
                self._docs_table.search()
                .limit(len(self._docs_table))
                .where(f"id = '{doc_id}'")
                .select(["metadata", "doc"])
                .to_list()
            )
            results.append(relevant_data)
        return results

    def get_relevant_qa_documents(self, question: str, k: int = None) -> List[str]:
        """
        Returns relevant question answers documents only
        Args:
            question (_type_): list of documents
        """
        return self.get_relevant_question_answers(question, k)["documents"][0]

    def get_relevant_docs_documents(self, question: str, k: int = None) -> List[str]:
        """
        Returns relevant question answers documents only
        Args:
            question (_type_): list of documents
        """
        return self.get_relevant_docs(question, k)["documents"][0]

    def _filter_docs_based_on_distance(
        self, documents: list, threshold: int
    ) -> List[str]:
        """
        Filter documents based on threshold
        Args:
            documents (List[str]): list of documents in string
            threshold (int): similarity threshold

        Returns:
            _type_: _description_
        """
        if not documents:
            return documents
        relevant_column = list(
            documents[0].keys() - {"id", "vector", "metadata", "_distance"}
        )

        filtered_data = [
            (
                document[relevant_column[0]],
                document["metadata"],
            )
            for document in documents
            if document["_distance"] < threshold
        ]

        return {
            key: [[data[i] for data in filtered_data]]
            for i, key in enumerate(["documents", "metadatas"])
        }
