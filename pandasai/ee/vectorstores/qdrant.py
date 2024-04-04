import logging
import uuid
from typing import Any, Dict, Iterable, List, Optional

import qdrant_client
from qdrant_client import models

from pandasai.helpers.logger import Logger
from pandasai.vectorstores.vectorstore import VectorStore

DEFAULT_COLLECTION_NAME = "pandasai"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
UUID_NAMESPACE = "f55f1395-e097-4f35-8c20-90fdea7baa14"


class Qdrant(VectorStore):
    """Implementation of VectorStore for Qdrant - https://qdrant.tech/

    Supports adding, updating, deleting and querying code Q/As and documents.\n
    Since Qdrant only allows unsigned integers or UUID strings as point IDs,
    we convert any arbitrary string ID into a UUID string based on a seed.

    Args:
        collection_name: Name of the collection.
        Will be transformed into `<COLLECTION_NAME>-qa` and `<COLLECTION_NAME>-docs` for code Q/A and documents respectively.\n
        embedding_model: Name of the embedding model to use.\n
        location:
            If `':memory:'` - use in-memory Qdrant instance.\n
            If `str` - use it as a `url` parameter.\n
            If `None` - use default values for `host` and `port`.\n
        url: either host or str of "`Optional[scheme]`, `host`, `Optional[port]`, `Optional[prefix]`". Default: `None`.\n
        port: Port of the REST API interface. Default: 6333.\n
        grpc_port: Port of the gRPC interface. Default: 6334.\n
        prefer_grpc: If `true` - use gPRC interface whenever possible in custom methods.\n
        https: If `true` - use HTTPS(SSL) protocol. Default: `None`.\n
        api_key: API key for authentication in Qdrant Cloud. Default: `None`.\n
        prefix:
            If not `None` - add `prefix` to the REST URL path.\n
            Example: `service/v1` will result in `http://localhost:6333/service/v1/[qdrant-endpoint]` for REST API.\n
            Default: `None`.\n
        timeout:
            Timeout for REST and gRPC API requests.\n
            Default: 5 seconds for REST and unlimited for gRPC.\n
        host: Host name of Qdrant service. If url and host are None, set to 'localhost'.\n
            Default: `None`.\n
        path: Persistence path for QdrantLocal. Default: `None`.\n
        grpc_options: Options for the low-level gRPC client, if used. Default: `None`.\n
        similary_threshold: Similarity threshold for search. Default: `None`.\n
        logger: Optional custom Logger instance..
    """

    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        location: Optional[str] = None,
        url: Optional[str] = None,
        port: Optional[int] = 6333,
        grpc_port: int = 6334,
        prefer_grpc: bool = False,
        https: Optional[bool] = None,
        api_key: Optional[str] = None,
        prefix: Optional[str] = None,
        timeout: Optional[int] = None,
        host: Optional[str] = None,
        path: Optional[str] = None,
        grpc_options: Optional[Dict[str, Any]] = None,
        similary_threshold: Optional[float] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        self._qa_collection_name = f"{collection_name}-qa"
        self._docs_collection_name = f"{collection_name}-docs"
        self._logger = logger or Logger()
        self._similarity_threshold = similary_threshold

        self._client = qdrant_client.QdrantClient(
            location=location,
            url=url,
            port=port,
            grpc_port=grpc_port,
            prefer_grpc=prefer_grpc,
            https=https,
            api_key=api_key,
            prefix=prefix,
            timeout=timeout,
            host=host,
            path=path,
            grpc_options=grpc_options,
        )
        self._client.set_model(embedding_model)

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
                f"Queries and codes length doesn't match. {len(queries)} != {len(codes)}"
            )

        qdrant_ids = self._convert_ids(ids) if ids else None

        qa_str = [self._format_qa(query, code) for query, code in zip(queries, codes)]

        # If IDs are not provided(None), qdrant_client generates random UUIDs
        return self._client.add(
            self._qa_collection_name,
            documents=qa_str,
            metadata=metadatas,
            ids=qdrant_ids,
        )

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
        qdrant_ids = self._convert_ids(ids) if ids else None

        # If IDs are not provided(None), qdrant_client generates random UUIDs
        return self._client.add(
            self._docs_collection_name,
            documents=docs,
            metadata=metadatas,
            ids=qdrant_ids,
        )

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

        if not (len(ids) == len(queries) == len(codes)):
            raise ValueError(
                f"Queries, codes and ids length doesn't match. {len(queries)} != {len(codes)} != {len(ids)}"
            )

        qdrant_ids = self._convert_ids(ids)

        # Ensure that the IDs exist in the collection
        if not self._validate_update_ids(self._qa_collection_name, qdrant_ids):
            return []

        qa_str = [self._format_qa(query, code) for query, code in zip(queries, codes)]

        # Entries with same IDs will be overwritten. Essentially updating them.
        return self._client.add(
            self._qa_collection_name,
            documents=qa_str,
            metadata=metadatas,
            ids=qdrant_ids,
        )

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

        if len(ids) != len(docs):
            raise ValueError(
                f"Docs and ids length doesn't match. {len(docs)} != {len(ids)}"
            )

        qdrant_ids = self._convert_ids(ids)

        # Ensure that the IDs exist in the collection
        if not self._validate_update_ids(self._qa_collection_name, qdrant_ids):
            return []

        # Entries with same IDs will be overwritten. Essentially updating them.
        return self._client.add(
            self._docs_collection_name,
            documents=docs,
            metadata=metadatas,
            ids=qdrant_ids,
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
        if ids:
            ids = self._convert_ids(ids)
            response = self._client.delete(
                self._qa_collection_name, points_selector=ids
            )
            return response.status == models.UpdateStatus.COMPLETED

    def delete_docs(self, ids: Optional[List[str]] = None) -> Optional[bool]:
        """
        Delete by vector ID to delete docs
        Args:
            ids: List of ids to delete

        Returns:
            Optional[bool]: True if deletion is successful,
            False otherwise
        """
        if ids:
            ids = self._convert_ids(ids)
            response = self._client.delete(
                self._docs_collection_name, points_selector=ids
            )
            return response.status == models.UpdateStatus.COMPLETED

    def delete_collection(self, collection_name: str) -> Optional[bool]:
        self._client.delete_collection(f"{collection_name}-qa")
        self._client.delete_collection(f"{collection_name}-docs")

    def get_relevant_question_answers(self, question: str, k: int = 1) -> List[dict]:
        """
        Returns relevant question answers based on search
        """
        response = self._client.query(
            self._qa_collection_name,
            query_text=question,
            limit=k,
            score_threshold=self._similarity_threshold,
        )

        return self._convert_query_response(response)

    def get_relevant_docs(self, question: str, k: int = 1) -> List[dict]:
        """
        Returns relevant documents based on semantic search
        """
        response = self._client.query(
            self._docs_collection_name,
            query_text=question,
            limit=k,
            score_threshold=self._similarity_threshold,
        )

        return self._convert_query_response(response)

    def get_relevant_question_answers_by_id(self, ids: Iterable[str]) -> List[dict]:
        """
        Returns question answers based on ids
        """

        qdrant_ids = self._convert_ids(ids)

        response = self._client.retrieve(self._qa_collection_name, ids=qdrant_ids)

        return self._convert_retrieve_response(response)

    def get_relevant_docs_by_id(self, ids: Iterable[str]) -> List[dict]:
        """
        Returns docs based on ids
        """

        qdrant_ids = self._convert_ids(ids)

        response = self._client.retrieve(self._docs_collection_name, ids=qdrant_ids)

        return self._convert_retrieve_response(response)

    def get_relevant_qa_documents(self, question: str, k: int = 1) -> List[str]:
        """
        Returns question answers documents only
        """
        return self.get_relevant_question_answers(question, k)["documents"]

    def get_relevant_docs_documents(self, question: str, k: int = 1) -> List[str]:
        """
        Returns question answers documents only
        """
        return self.get_relevant_docs(question, k)["documents"]

    def _validate_update_ids(self, collection_name: str, ids: List[str]) -> bool:
        """
        Validates all the IDs exist in the collection
        """
        retrieved_ids = [
            point.id
            for point in self._client.retrieve(
                collection_name, ids=ids, with_payload=False, with_vectors=False
            )
        ]

        if missing_ids := set(ids) - set(retrieved_ids):
            self._logger.log(
                f"Missing IDs: {missing_ids}. Skipping update", level=logging.WARN
            )
            return False

        return True

    def _convert_ids(self, ids: Iterable[str]) -> List[str]:
        """
        Converts any string into a UUID string based on a seed.

        Qdrant accepts UUID strings and unsigned integers as point ID.
        We use a seed to convert each string into a UUID string deterministically.
        This allows us to overwrite the same point with the original ID.
        """
        return [
            id
            if self._is_valid_uuid(id)
            else str(uuid.uuid5(uuid.UUID(UUID_NAMESPACE), id))
            for id in ids
        ]

    def _convert_query_response(
        self, results: List[models.QueryResponse]
    ) -> List[dict]:
        documents, distances, metadatas, ids = [], [], [], []

        for point in results:
            documents.append(point.document)
            distances.append(point.score)
            metadatas.append(point.metadata)
            ids.append(point.id)

        return {
            "documents": documents,
            "distances": distances,
            "metadatas": metadatas,
            "ids": ids,
        }

    def _convert_retrieve_response(self, response: List[models.Record]) -> List[dict]:
        documents, metadatas, ids = [], [], []

        for point in response:
            documents.append(point.payload.get("document", ""))
            metadatas.append(point.payload)
            ids.append(point.id)

        return {
            "documents": documents,
            "metadatas": metadatas,
            "ids": ids,
        }

    def _is_valid_uuid(self, id: str):
        try:
            uuid.UUID(id)
            return True
        except ValueError:
            return False
