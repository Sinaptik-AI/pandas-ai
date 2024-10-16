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
        if len(queries) != len(codes):
            raise ValueError(
                f"Queries and codes length doesn't match. {len(queries)} != {len(codes)}"
            )

        qdrant_ids = self._convert_ids(ids) if ids else None

        qa_str = [self._format_qa(query, code) for query, code in zip(queries, codes)]

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
        qdrant_ids = self._convert_ids(ids) if ids else None

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
        if not (len(ids) == len(queries) == len(codes)):
            raise ValueError(
                f"Queries, codes and ids length doesn't match. {len(queries)} != {len(codes)} != {len(ids)}"
            )

        qdrant_ids = self._convert_ids(ids)

        if not self._validate_update_ids(self._qa_collection_name, qdrant_ids):
            return []

        qa_str = [self._format_qa(query, code) for query, code in zip(queries, codes)]

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
        if len(ids) != len(docs):
            raise ValueError(
                f"Docs and ids length doesn't match. {len(docs)} != {len(ids)}"
            )

        qdrant_ids = self._convert_ids(ids)

        if not self._validate_update_ids(self._qa_collection_name, qdrant_ids):
            return []

        return self._client.add(
            self._docs_collection_name,
            documents=docs,
            metadata=metadatas,
            ids=qdrant_ids,
        )

    def delete_question_and_answers(
        self, ids: Optional[List[str]] = None
    ) -> Optional[bool]:
        if ids:
            ids = self._convert_ids(ids)
            response = self._client.delete(
                self._qa_collection_name, points_selector=ids
            )
            return response.status == models.UpdateStatus.COMPLETED

    def delete_docs(self, ids: Optional[List[str]] = None) -> Optional[bool]:
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
        if not self._client.collection_exists(self._qa_collection_name):
            return {
                "documents": [],
                "distances": [],
                "metadatas": [],
                "ids": [],
            }

        response = self._client.query(
            self._qa_collection_name,
            query_text=question,
            limit=k,
            score_threshold=self._similarity_threshold,
        )

        return self._convert_query_response(response)

    def get_relevant_docs(self, question: str, k: int = 1) -> List[dict]:
        if not self._client.collection_exists(self._docs_collection_name):
            return {
                "documents": [],
                "distances": [],
                "metadatas": [],
                "ids": [],
            }
        response = self._client.query(
            self._docs_collection_name,
            query_text=question,
            limit=k,
            score_threshold=self._similarity_threshold,
        )
        return self._convert_query_response(response)

    def get_relevant_question_answers_by_id(self, ids: Iterable[str]) -> List[dict]:
        qdrant_ids = self._convert_ids(ids)

        response = self._client.retrieve(self._qa_collection_name, ids=qdrant_ids)

        return self._convert_retrieve_response(response)

    def get_relevant_docs_by_id(self, ids: Iterable[str]) -> List[dict]:
        qdrant_ids = self._convert_ids(ids)

        response = self._client.retrieve(self._docs_collection_name, ids=qdrant_ids)

        return self._convert_retrieve_response(response)

    def get_relevant_qa_documents(self, question: str, k: int = 1) -> List[str]:
        return self.get_relevant_question_answers(question, k)["documents"]

    def get_relevant_docs_documents(self, question: str, k: int = 1) -> List[str]:
        return self.get_relevant_docs(question, k)["documents"]

    def _validate_update_ids(self, collection_name: str, ids: List[str]) -> bool:
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
        return [
            (
                id
                if self._is_valid_uuid(id)
                else str(uuid.uuid5(uuid.UUID(UUID_NAMESPACE), id))
            )
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
