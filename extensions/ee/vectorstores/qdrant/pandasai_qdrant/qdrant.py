import logging
import uuid
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import qdrant_client
from qdrant_client import models

from pandasai.helpers.logger import Logger
from pandasai.vectorstores.vectorstore import VectorStore

DEFAULT_COLLECTION_NAME = "pandasai"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
UUID_NAMESPACE = "f55f1395-e097-4f35-8c20-90fdea7baa14"


class Qdrant(VectorStore):
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
    ):
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in queries]

        if metadatas is None:
            metadatas = [{} for _ in queries]

        # Generate dummy vectors for testing
        vectors = [np.zeros(512) for _ in queries]

        points = [
            models.PointStruct(
                id=self._convert_ids([id])[0],
                vector=vector.tolist(),
                payload={
                    "document": query,
                    "code": code,
                    "metadata": metadata,
                },
            )
            for query, code, id, metadata, vector in zip(
                queries, codes, ids, metadatas, vectors
            )
        ]

        self._client.upsert(collection_name=self._qa_collection_name, points=points)

    def add_docs(
        self,
        docs: Iterable[str],
        ids: Optional[Iterable[str]] = None,
        metadatas: Optional[List[dict]] = None,
    ):
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in docs]

        if metadatas is None:
            metadatas = [{} for _ in docs]

        # Generate dummy vectors for testing
        vectors = [np.zeros(512) for _ in docs]

        points = [
            models.PointStruct(
                id=self._convert_ids([id])[0],
                vector=vector.tolist(),
                payload={
                    "document": doc,
                    "metadata": metadata,
                },
            )
            for doc, id, metadata, vector in zip(docs, ids, metadatas, vectors)
        ]

        self._client.upsert(collection_name=self._docs_collection_name, points=points)

    def update_question_answer(
        self,
        ids: Iterable[str],
        queries: Iterable[str],
        codes: Iterable[str],
        metadatas: Optional[List[dict]] = None,
    ):
        if metadatas is None:
            metadatas = [{} for _ in queries]

        self._validate_update_ids(self._qa_collection_name, list(ids))

        # Generate dummy vectors for testing
        vectors = [np.zeros(512) for _ in queries]

        points = [
            models.PointStruct(
                id=self._convert_ids([id])[0],
                vector=vector.tolist(),
                payload={
                    "document": query,
                    "code": code,
                    "metadata": metadata,
                },
            )
            for query, code, id, metadata, vector in zip(
                queries, codes, ids, metadatas, vectors
            )
        ]

        self._client.upsert(collection_name=self._qa_collection_name, points=points)

    def update_docs(
        self,
        ids: Iterable[str],
        docs: Iterable[str],
        metadatas: Optional[List[dict]] = None,
    ):
        if metadatas is None:
            metadatas = [{} for _ in docs]

        self._validate_update_ids(self._docs_collection_name, list(ids))

        # Generate dummy vectors for testing
        vectors = [np.zeros(512) for _ in docs]

        points = [
            models.PointStruct(
                id=self._convert_ids([id])[0],
                vector=vector.tolist(),
                payload={
                    "document": doc,
                    "metadata": metadata,
                },
            )
            for doc, id, metadata, vector in zip(docs, ids, metadatas, vectors)
        ]

        self._client.upsert(collection_name=self._docs_collection_name, points=points)

    def delete_question_and_answers(self, ids: Optional[List[str]] = None):
        if ids is not None:
            self._client.delete(
                collection_name=self._qa_collection_name,
                points_selector=models.PointIdsList(
                    points=self._convert_ids(ids),
                ),
            )
        else:
            self.delete_collection(self._qa_collection_name)

    def delete_docs(self, ids: Optional[List[str]] = None):
        if ids is not None:
            self._client.delete(
                collection_name=self._docs_collection_name,
                points_selector=models.PointIdsList(
                    points=self._convert_ids(ids),
                ),
            )
        else:
            self.delete_collection(self._docs_collection_name)

    def delete_collection(self, collection_name: str):
        try:
            self._client.delete_collection(collection_name=collection_name)
        except Exception as e:
            logging.warning(f"Failed to delete collection {collection_name}: {e}")

    def get_relevant_question_answers(self, question: str, k: int = 1):
        results = self._client.search(
            collection_name=self._qa_collection_name,
            query_text=question,
            limit=k,
            score_threshold=self._similarity_threshold,
        )
        return self._convert_query_response(results)

    def get_relevant_docs(self, question: str, k: int = 1):
        results = self._client.search(
            collection_name=self._docs_collection_name,
            query_text=question,
            limit=k,
            score_threshold=self._similarity_threshold,
        )
        return self._convert_query_response(results)

    def get_relevant_question_answers_by_id(self, ids: Iterable[str]):
        response = self._client.retrieve(
            collection_name=self._qa_collection_name,
            ids=self._convert_ids(ids),
        )
        return self._convert_retrieve_response(response)

    def get_relevant_docs_by_id(self, ids: List[str]) -> Dict[str, List[Any]]:
        """Get relevant documents by IDs"""
        if not ids:
            return {
                "documents": [],
                "metadatas": [],
                "ids": [],
            }

        if points := self._client.retrieve(
            collection_name=self._docs_collection_name,
            ids=ids,
            with_payload=True,
            with_vectors=True,
        ):
            documents = [point.payload["document"] for point in points]
            metadatas = [point.payload for point in points]
            ids = [str(point.id) for point in points]

            return {
                "documents": documents,
                "metadatas": metadatas,
                "ids": ids,
            }

        return {
            "documents": [],
            "metadatas": [],
            "ids": [],
        }

    def get_relevant_qa_documents(self, question: str, k: int = 1):
        results = self._client.search(
            collection_name=self._qa_collection_name,
            query_text=question,
            limit=k,
            score_threshold=self._similarity_threshold,
        )
        return self._convert_query_response(results)

    def get_relevant_docs_documents(self, question: str, k: int = 1):
        results = self._client.search(
            collection_name=self._docs_collection_name,
            query_text=question,
            limit=k,
            score_threshold=self._similarity_threshold,
        )
        return self._convert_query_response(results)

    def _validate_update_ids(self, collection_name: str, ids: List[str]) -> None:
        """Validate that all IDs to be updated exist in the collection.

        Args:
            collection_name: Name of the collection to validate IDs against
            ids: List of IDs to validate

        Raises:
            ValueError: If any of the IDs are not found in the collection
        """
        if not ids:
            return

        if not (
            response := self._client.retrieve(
                collection_name=collection_name,
                ids=(converted_ids := self._convert_ids(ids)),
            )
        ):
            raise ValueError("No IDs found in the collection")

        found_ids = {str(point.id) for point in response}
        if missing := [
            id
            for id, conv_id in zip(ids, converted_ids)
            if str(conv_id) not in found_ids
        ]:
            raise ValueError(f"IDs not found in collection: {missing}")

    def _convert_ids(self, ids: Iterable[str]):
        return [
            (
                id
                if self._is_valid_uuid(id)
                else str(uuid.uuid5(uuid.UUID(UUID_NAMESPACE), id))
            )
            for id in ids
        ]

    def _convert_query_response(self, results: List[models.ScoredPoint]) -> List[dict]:
        documents, distances, metadatas, ids = [], [], [], []

        for point in results:
            documents.append(point.payload.get("document", ""))
            distances.append(point.score)
            metadatas.append(point.payload)
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
