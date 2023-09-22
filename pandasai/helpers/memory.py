""" Memory class to store the conversations """


class Memory:
    """Memory class to store the conversations"""

    _messages: list
    _memory_size: int

    def __init__(self, memory_size: int = 1):
        self._messages = []
        self._memory_size = memory_size

    def add(self, message: str, is_user: bool):
        self._messages.append({"message": message, "is_user": is_user})

    def count(self) -> int:
        return len(self._messages)

    def all(self) -> list:
        return self._messages

    def last(self) -> dict:
        return self._messages[-1]

    def get_conversation(self, limit: int = None) -> str:
        """
        Returns the conversation messages based on limit parameter
        or default memory size
        """
        limit = self._memory_size if limit is None else limit
        return "\n".join(
            [
                f"{f'User {i+1}' if message['is_user'] else f'Assistant {i}'}: "
                f"{message['message']}"
                for i, message in enumerate(self._messages[-limit:])
            ]
        )

    def clear(self):
        self._messages = []
