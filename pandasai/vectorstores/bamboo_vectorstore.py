from typing import Iterable, List, Optional, Union

from pandasai.helpers.logger import Logger
from pandasai.helpers.request import Session
from pandasai.vectorstores.vectorstore import VectorStore


class BambooVectorStore(VectorStore):
    """
    Implementation of ChromeDB vector store
    """

    _logger: Logger

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        api_key: Optional[str] = None,
        logger: Optional[Logger] = None,
        max_samples: int = 1,
    ) -> None:
        self._max_samples = max_samples
        self._logger = logger or Logger()
        self._session = Session(endpoint_url, api_key, logger)

    def add_question_answer(self, queries: Iterable[str], codes: Iterable[str]) -> bool:
        """
        Add question and answer(code) to the training set
        Args:
            queries: string of question
            codes: str
        """
        self._session.post("/training-data", json={"query": queries, "code": codes})
        return True

    def add_docs(self, docs: Iterable[str]) -> bool:
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
        self._session.post("/training-docs", json={"docs": docs})
        return True

    def get_relevant_qa_documents(self, question: str, k: int = None) -> List[dict]:
        """
        Returns relevant question answers based on search
        """
        k = k or self._max_samples
        docs = self._session.get(
            "/training-data/qa/relevant-qa", params={"query": question, "count": k}
        )
        return docs["docs"]

    def get_relevant_docs_documents(
        self, question: str, k: Union[int, None] = 3
    ) -> List[str]:
        """
        Returns relevant question answers documents only
        Args:
            question (_type_): list of documents
        """
        k = k or self._max_samples

        docs = self._session.get(
            "/training-docs/docs/relevant-docs", params={"query": question, "count": k}
        )
        return docs["docs"]
