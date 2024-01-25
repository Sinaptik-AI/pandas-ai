import os
from typing import Callable, Iterable, List, Optional, Union
import uuid
from pandasai.helpers.logger import Logger
from pandasai.helpers.path import find_project_root
from pandasai.vectorstores import VectorStore
import chromadb
import chromadb.config
from chromadb.utils import embedding_functions

DEFAULT_EMBEDDING_FUNCTION = embedding_functions.DefaultEmbeddingFunction()


class Chroma(VectorStore):
    """
    Implementation of ChromeDB vector store
    """

    _logger: Logger

    def __init__(
        self,
        collection_name: str = "pandasai",
        embedding_function: Optional[Callable[[List[str]], List[float]]] = None,
        persist_path: Optional[str] = None,
        client_settings: Optional[chromadb.config.Settings] = None,
        max_samples: int = 3,
        similary_threshold: int = 1.5,
        logger: Optional[Logger] = None,
    ) -> None:
        self._logger = logger or Logger()
        self._max_samples = max_samples
        self._similarity_threshold = similary_threshold

        # Initialize Chromadb Client
        # initialize from client settings if exists
        if client_settings:
            client_settings.persist_directory = (
                persist_path or client_settings.persist_directory
            )
            _client_settings = client_settings

        # use persist path if exists
        elif persist_path:
            _client_settings = chromadb.config.Settings(
                is_persistent=True, anonymized_telemetry=False
            )
            _client_settings.persist_directory = persist_path
        # else use root as default path
        else:
            _client_settings = chromadb.config.Settings(
                is_persistent=True, anonymized_telemetry=False
            )
            _client_settings.persist_directory = os.path.join(
                find_project_root(), "chromadb"
            )

        self._client_settings = _client_settings
        self._client = chromadb.Client(_client_settings)
        self._persist_directory = _client_settings.persist_directory

        self._logger.log(f"Persisting Agent Training data in {self._persist_directory}")

        self._embedding_function = embedding_function or DEFAULT_EMBEDDING_FUNCTION

        self._qa_collection = self._client.get_or_create_collection(
            name=f"{collection_name}-qa", embedding_function=self._embedding_function
        )

        self._docs_collection = self._client.get_or_create_collection(
            name=f"{collection_name}-docs", embedding_function=self._embedding_function
        )

        self._logger.log(f"Successfully initialized collection {collection_name}")

    def add_question_answer(
        self,
        queries: Iterable[str],
        codes: Iterable[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Add question and answer(code) to the training set
        Args:
            query: string of question
            code: str
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters
        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        if len(queries) != len(codes):
            raise ValueError(
                f"Queries and codes dimension doesn't match {len(queries)} != {len(codes)}"
            )

        ids = [f"{str(uuid.uuid4())}-qa" for _ in queries]
        qa_str = [self._format_qa(query, code) for query, code in zip(queries, codes)]

        self._qa_collection.add(
            documents=qa_str,
            metadatas=metadatas,
            ids=ids,
        )

    def add_docs(
        self,
        docs: Iterable[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Add docs to the training set
        Args:
            docs: Iterable of strings to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            kwargs: vectorstore specific parameters

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        ids = [f"{str(uuid.uuid4())}-docs" for _ in docs]
        self._docs_collection.add(
            documents=docs,
            metadatas=metadatas,
            ids=ids,
        )

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
        self._qa_collection.delete(ids=ids)
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
        self._docs_collection.delete(ids=ids)
        return True

    def get_relevant_question_answers(
        self, question: str, k: Union[int, None] = None
    ) -> List[dict]:
        """
        Returns relevant question answers based on search
        """
        k = k or self._max_samples

        relevant_data: chromadb.QueryResult = self._qa_collection.query(
            query_texts=question,
            n_results=k,
            include=["metadatas", "documents", "distances"],
        )

        return self._filter_docs_based_on_distance(
            relevant_data, self._similarity_threshold
        )

    def get_relevant_docs(self, question: str, k: int = 3) -> List[dict]:
        """
        Returns relevant documents based search
        """
        k = k or self._max_samples

        relevant_data: chromadb.QueryResult = self._docs_collection.query(
            query_texts=question,
            n_results=k,
            include=["metadatas", "documents", "distances"],
        )

        return self._filter_docs_based_on_distance(
            relevant_data, self._similarity_threshold
        )

    def get_relevant_qa_documents(self, question: str, k: int = 3) -> List[str]:
        """
        Returns relevant question answers documents only
        Args:
            question (_type_): list of documents
        """
        return self.get_relevant_question_answers(question, k)["documents"][0]

    def get_relevant_docs_documents(self, question: str, k: int = 3) -> List[str]:
        """
        Returns relevant question answers documents only
        Args:
            question (_type_): list of documents
        """
        return self.get_relevant_docs(question, k)["documents"][0]

    def _filter_docs_based_on_distance(
        self, documents: chromadb.QueryResult, threshold: int
    ) -> List[str]:
        """
        Filter documents based on threshold
        Args:
            documents (List[str]): list of documents in string
            distances (List[float]): list of distances in float
            threshold (int): similarity threshold

        Returns:
            _type_: _description_
        """
        filtered_data = [
            (doc, distance, metadata)
            for doc, distance, metadata in zip(
                documents["documents"][0],
                documents["distances"][0],
                documents["metadatas"][0],
            )
            if distance < threshold
        ]

        return {
            key: [[data[i] for data in filtered_data]]
            for i, key in enumerate(["documents", "distances", "metadatas"])
        }
