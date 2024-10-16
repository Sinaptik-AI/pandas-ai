import logging
import uuid
from typing import Dict, Iterable, List, Optional

from pydantic import Field
from pymilvus import DataType, MilvusClient, model

from pandasai.helpers.logger import Logger
from pandasai.vectorstores.vectorstore import VectorStore

DEFAULT_COLLECTION_NAME = "pandasai"
UUID_NAMESPACE = "f55f1395-e097-4f35-8c20-90fdea7baa14"
ID = "id"
EMBEDDING = "vector"
DOCUMENT = "document"
URI = "milvus_demo.db"


class Milvus(VectorStore):
    qa_dimension: int = Field(
        default=384, description="default embedding model dimension"
    )

    docs_dimension: int = Field(
        default=384, description="default embedding model dimension"
    )

    # Initializes the Milvus object with collection names, a URI for the Milvus database,
    # a logger, and the embedding function.
    def __init__(
        self,
        collection_name: Optional[str] = DEFAULT_COLLECTION_NAME,
        uri: Optional[str] = URI,
        similarity_threshold: Optional[float] = None,
        logger: Optional[Logger] = None,
    ):
        self.docs_collection_name = f"{collection_name}_docs"
        self.qa_collection_name = f"{collection_name}_qa"
        self.uri = uri
        self._logger = logger or Logger()
        self.similarity_threshold = similarity_threshold
        self.emb_function = model.DefaultEmbeddingFunction()
        self.client = MilvusClient(uri=self.uri)

    # Adds question-answer pairs to the Milvus collection.
    # It takes queries (questions), codes (answers), optional IDs, and metadata.
    # If queries and codes have mismatched lengths, it raises a ValueError.
    # The embeddings are calculated, and data is inserted into the QA collection.
    def add_question_answer(
        self,
        queries: Iterable[str],
        codes: Iterable[str],
        ids: Iterable[str] = None,
        metadatas: List[Dict] = None,
    ) -> List[str]:
        if len(queries) != len(codes):
            raise ValueError(
                f"Queries and codes length doesn't match. {len(queries)} != {len(codes)}"
            )
        format_qa = [
            self._format_qa(query, code) for query, code in zip(queries, codes)
        ]
        vectors = self.emb_function.encode_documents(format_qa)
        self.qa_dimension = self.emb_function.dim
        milvus_ids = (
            self._convert_ids(ids) if ids else self.generate_random_uuids(len(queries))
        )

        if not self.client.has_collection(collection_name=self.qa_collection_name):
            self._initiate_qa_collection()

        if metadatas:
            data = [
                {ID: id, EMBEDDING: vector, DOCUMENT: doc, "metadata": metadata}
                for id, vector, doc, metadata in zip(
                    milvus_ids, vectors, format_qa, metadatas
                )
            ]
        else:
            data = [
                {ID: id, EMBEDDING: vector, DOCUMENT: doc}
                for id, vector, doc in zip(milvus_ids, vectors, format_qa)
            ]

        self.client.insert(
            collection_name=self.qa_collection_name,
            data=data,
        )
        return milvus_ids

    # Adds documents to the Milvus collection.
    # It accepts documents, optional IDs, and metadata, and stores them in the document collection.
    def add_docs(
        self,
        docs: Iterable[str],
        ids: Iterable[str] = None,
        metadatas: List[Dict] = None,
    ) -> List[str]:
        milvus_ids = (
            self._convert_ids(ids) if ids else self.generate_random_uuids(len(docs))
        )
        vectors = self.emb_function.encode_documents(docs)

        if not self.client.has_collection(collection_name=self.docs_collection_name):
            self._initiate_docs_collection()

        if metadatas:
            data = [
                {ID: id, EMBEDDING: vector, DOCUMENT: doc, "metadata": metadata}
                for id, vector, doc, metadata in zip(
                    milvus_ids, vectors, docs, metadatas
                )
            ]
        else:
            data = [
                {ID: id, EMBEDDING: vector, DOCUMENT: doc}
                for id, vector, doc in zip(milvus_ids, vectors, docs)
            ]

        self.client.insert(
            collection_name=self.docs_collection_name,
            data=data,
        )

        return milvus_ids

    # Retrieves the most relevant question-answer pairs from the QA collection
    # based on a given query and returns the top-k results.
    def get_relevant_question_answers(self, question: str, k: int = 1) -> List[Dict]:
        if not self.client.has_collection(collection_name=self.qa_collection_name):
            return {
                "documents": [],
                "distances": [],
                "metadatas": [],
                "ids": [],
            }

        vector = self.emb_function.encode_documents(question)
        response = self.client.search(
            collection_name=self.qa_collection_name,
            data=vector,
            limit=k,
            filter="",
            output_fields=[DOCUMENT],
        )
        return self._convert_search_response(response)

    # Retrieves the most relevant documents from the document collection
    # based on a given query and returns the top-k results.
    def get_relevant_docs(self, question: str, k: int = 1) -> List[Dict]:
        if not self.client.has_collection(collection_name=self.docs_collection_name):
            return {
                "documents": [],
                "distances": [],
                "metadatas": [],
                "ids": [],
            }
        vector = self.emb_function.encode_documents(question)
        response = self.client.search(
            collection_name=self.docs_collection_name,
            data=vector,
            limit=k,
            output_fields=[DOCUMENT],
        )
        return self._convert_search_response(response)

    # Converts the search response returned by Milvus into a list of dictionaries
    # with document content, ids, metadata, and distances.
    def _convert_search_response(self, response):
        document = []
        ids = []
        metadatas = []
        distances = []

        for res in response[0]:
            document.append(res["entity"][DOCUMENT])
            ids.append(res[ID])
            if "metadata" in res["entity"]:
                metadatas.append(res["entity"]["metadata"])
            distances.append(res["distance"])

        return {
            "documents": document,
            "distances": distances,
            "metadatas": metadatas,
            "ids": ids,
        }

    # Creates the QA collection schema and defines the fields to store question-answer pairs,
    # including ID, embeddings, and document content.
    def _initiate_qa_collection(self):
        schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=True,
        )
        schema.add_field(
            field_name=ID, datatype=DataType.VARCHAR, max_length=1000, is_primary=True
        )
        schema.add_field(
            field_name=EMBEDDING, datatype=DataType.FLOAT_VECTOR, dim=self.qa_dimension
        )
        schema.add_field(
            field_name=DOCUMENT, datatype=DataType.VARCHAR, max_length=1000
        )

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name=ID,
        )
        index_params.add_index(
            field_name=EMBEDDING,
            metric_type="COSINE",
        )
        self.client.create_collection(
            collection_name=self.qa_collection_name,
            schema=schema,
            index_params=index_params,
        )

    # Creates the document collection schema and defines the fields to store documents,
    # including ID, embeddings, and document content.
    def _initiate_docs_collection(self):
        schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=True,
        )
        schema.add_field(field_name=ID, datatype=DataType.VARCHAR, is_primary=True)
        schema.add_field(
            field_name=EMBEDDING,
            datatype=DataType.FLOAT_VECTOR,
            dim=self.docs_dimension,
        )
        schema.add_field(
            field_name=DOCUMENT, datatype=DataType.VARCHAR, max_length=1000
        )

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name=ID,
        )
        index_params.add_index(
            field_name=EMBEDDING,
            metric_type="COSINE",
        )
        self.client.create_collection(
            collection_name=self.docs_collection_name,
            schema=schema,
            index_params=index_params,
        )

    # Returns the list of relevant document contents from the document collection
    # based on a given query and the top-k results.
    def get_relevant_docs_documents(self, question: str, k: int = 1) -> List[str]:
        return self.get_relevant_docs(question, k)["documents"]

    # Returns the list of relevant question-answer document contents from the QA collection
    # based on a given query and the top-k results.
    def get_relevant_qa_documents(self, question: str, k: int = 1) -> List[str]:
        return self.get_relevant_question_answers(question, k)["documents"]

    # Retrieves question-answer documents by their IDs and returns the corresponding documents.
    def get_relevant_question_answers_by_id(self, ids: Iterable[str]) -> List[Dict]:
        milvus_ids = self._convert_ids(ids)
        response = self.client.query(
            collection_name=self.qa_collection_name,
            ids=milvus_ids,
            output_fields=[DOCUMENT, ID, "distance", "entity"],
        )
        return self._convert_search_response(response)["documents"]

    # Deletes documents from the document collection based on a list of document IDs.
    def delete_docs(self, ids: List[str] = None) -> bool:
        milvus_ids = self._convert_ids(ids)
        id_filter = str(milvus_ids)
        self.client.delete(
            collection_name=self.docs_collection_name,
            filter=f"id in {id_filter}",
        )
        return True

    # Deletes question-answer pairs from the QA collection based on a list of question-answer IDs.
    def delete_question_and_answers(self, ids: List[str] = None) -> bool:
        milvus_ids = self._convert_ids(ids)
        id_filter = str(milvus_ids)
        self.client.delete(
            collection_name=self.qa_collection_name,
            filter=f"id in {id_filter}",
        )
        return True

    # Updates the existing question-answer pairs in the QA collection based on given IDs.
    # This replaces the question-answer text and embeddings, and allows optional metadata.
    def update_question_answer(
        self,
        ids: Iterable[str],
        queries: Iterable[str],
        codes: Iterable[str],
        metadatas: List[Dict] = None,
    ) -> List[str]:
        if not (len(ids) == len(queries) == len(codes)):
            raise ValueError(
                f"Queries, codes and ids length doesn't match. {len(queries)} != {len(codes)} != {len(ids)}"
            )
        milvus_ids = self._convert_ids(ids)
        if not self._validate_update_ids(
            collection_name=self.qa_collection_name, ids=milvus_ids
        ):
            return []

        format_qa = [
            self._format_qa(query, code) for query, code in zip(queries, codes)
        ]
        vectors = self.emb_function.encode_documents(format_qa)
        data = [
            {ID: id, EMBEDDING: vector, DOCUMENT: doc}
            for id, vector, doc in zip(milvus_ids, vectors, format_qa)
        ]

        self.client.insert(
            collection_name=self.qa_collection_name,
            data=data,
        )

    # Updates the existing documents in the document collection based on given IDs.
    # This replaces the document text and embeddings, and allows optional metadata.
    def update_docs(
        self, ids: Iterable[str], docs: Iterable[str], metadatas: List[Dict] = None
    ) -> List[str]:
        if not (len(ids) == len(docs)):
            raise ValueError(
                f"Queries, codes and ids length doesn't match. {len(id)} != {len(docs)}"
            )
        milvus_ids = self._convert_ids(ids)
        if not self._validate_update_ids(
            collection_name=self.docs_collection_name, ids=milvus_ids
        ):
            return []

        vectors = self.emb_function.encode_document(docs)
        data = [
            {ID: id, EMBEDDING: vector, DOCUMENT: doc}
            for id, vector, doc in zip(milvus_ids, vectors, docs)
        ]

        return self.client.insert(collection_name=self.docs_collection_name, data=data)

    # Validates that the given IDs exist in the collection.
    # Returns True if all IDs are present, otherwise logs the missing IDs and returns False.
    def _validate_update_ids(self, collection_name: str, ids: List[str]) -> bool:
        response = self.client.query(collection_name=collection_name, ids=ids)
        retrieved_ids = [p["id"] for p in response[0]]
        diff = set(ids) - set(retrieved_ids)
        if diff:
            self._logger.log(
                f"Missing IDs: {diff}. Skipping update", level=logging.WARN
            )
            return False
        return True

    # Deletes the QA and document collections for a given collection name.
    def delete_collection(self, collection_name: str) -> Optional[bool]:
        self.client.drop_collection(collection_name=f"{collection_name}-qa")
        self.client.drop_collection(collection_name=f"{collection_name}-docs")

    # Converts given IDs to UUIDs using a namespace.
    # If the ID is already a valid UUID, it returns the ID unchanged.
    def _convert_ids(self, ids: Iterable[str]) -> List[str]:
        return [
            id
            if self._is_valid_uuid(id)
            else str(uuid.uuid5(uuid.UUID(UUID_NAMESPACE), id))
            for id in ids
        ]

    # Checks if a given ID is a valid UUID.
    def _is_valid_uuid(self, id: str):
        try:
            uuid.UUID(id)
            return True
        except ValueError:
            return False

    # Generates a list of random UUIDs.
    def generate_random_uuids(self, n):
        return [str(uuid.uuid4()) for _ in range(n)]
