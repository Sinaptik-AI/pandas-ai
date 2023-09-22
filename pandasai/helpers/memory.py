""" Memory class to store the conversations """
import sys


class Memory:
    """Memory class to store the conversations"""

    _messages: list
    _max_messages: int

    def __init__(self, max_messages: int = sys.maxsize):
        self._messages = []
        self._max_messages = max_messages

    def add(self, message: str, is_user: bool):
        self._messages.append({"message": message, "is_user": is_user})

        # Delete two entry because of the conversation
        if len(self._messages) > self._max_messages:
            del self._messages[:2]

    def count(self) -> int:
        return len(self._messages)

    def all(self) -> list:
        return self._messages

    def last(self) -> dict:
        return self._messages[-1]

    def get_conversation(self, limit: int = 1) -> str:
        return "\n".join(
            [
                f"{f'User {i+1}' if message['is_user'] else f'Assistant {i}'}: "
                f"{message['message']}"
                for i, message in enumerate(self._messages[-limit:])
            ]
        )

    def clear(self):
        self._messages = []
