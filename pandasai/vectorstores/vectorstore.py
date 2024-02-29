from abc import ABC, abstractmethod
from typing import Iterable, List, Optional


class VectorStore(ABC):
    """Interface for vector store."""

    @abstractmethod
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
        raise NotImplementedError(
            "add_question_answer method must be implemented by subclass."
        )

    @abstractmethod
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
        raise NotImplementedError("add_docs method must be implemented by subclass.")

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
        pass

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
        pass

    def delete_question_and_answers(
        self, ids: Optional[List[str]] = None
    ) -> Optional[bool]:
        """
        Delete by vector ID or other criteria.
        Args:
            ids: List of ids to delete

        Returns:
            Optional[bool]: True if deletion is successful,
            False otherwise
        """
        raise NotImplementedError(
            "delete_question_and_answers method must be implemented by subclass."
        )

    def delete_docs(self, ids: Optional[List[str]] = None) -> Optional[bool]:
        """
        Delete by vector ID or other criteria.
        Args:
            ids: List of ids to delete

        Returns:
            Optional[bool]: True if deletion is successful,
            False otherwise
        """
        raise NotImplementedError("delete_docs method must be implemented by subclass.")

    def delete_collection(self, collection_name: str) -> Optional[bool]:
        """
        Delete the collection
        Args:
            collection_name (str): name of the collection

        Returns:
            Optional[bool]: _description_
        """

    def get_relevant_question_answers(self, question: str, k: int = 1) -> List[dict]:
        """
        Returns relevant question answers based on search
        """
        raise NotImplementedError(
            "get_relevant_question_answers method must be implemented by subclass."
        )

    def get_relevant_docs(self, question: str, k: int = 1) -> List[dict]:
        """
        Returns relevant documents based search
        """
        raise NotImplementedError(
            "get_relevant_docs method must be implemented by subclass."
        )

    def get_relevant_question_answers_by_id(self, ids: Iterable[str]) -> List[dict]:
        """
        Returns relevant question answers based on ids
        """
        pass

    def get_relevant_docs_by_id(self, ids: Iterable[str]) -> List[dict]:
        """
        Returns relevant documents based on ids
        """
        pass

    @abstractmethod
    def get_relevant_qa_documents(self, question: str, k: int = 1) -> List[str]:
        """
        Returns relevant question answers documents only
        Args:
            question (_type_): list of documents
        """
        raise NotImplementedError(
            "get_relevant_qa_documents method must be implemented by subclass."
        )

    @abstractmethod
    def get_relevant_docs_documents(self, question: str, k: int = 1) -> List[str]:
        """
        Returns relevant question answers documents only
        Args:
            question (_type_): list of documents
        """
        raise NotImplementedError(
            "get_relevant_docs_documents method must be implemented by subclass."
        )

    def _format_qa(self, query: str, code: str) -> str:
        return f"Q: {query}\n A: {code}"
