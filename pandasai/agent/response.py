from typing import List


class ClarificationResponse:
    """
    Clarification Response

    """

    def __init__(
        self, success: bool = True, questions: List[str] = [], message: str = ""
    ):
        """
        Args:
            success: Whether the response generated or not.
            questions: List of questions
        """
        self._success: bool = success
        self._questions: List[str] = questions
        self._message: str = message

    @property
    def questions(self) -> List[str]:
        return self._questions

    @property
    def message(self) -> str:
        return self._message

    @property
    def success(self) -> bool:
        return self._success

    def __bool__(self) -> bool:
        """
        Define the success of response.
        """
        return self._success
