""" Memory class to store the conversations """


class Memory:
    """Memory class to store the conversations"""

    _messages: list

    def __init__(self):
        self._messages = []

    def add(self, message: str, is_user: bool):
        self._messages.append({"message": message, "is_user": is_user})

    def count(self) -> int:
        return len(self._messages)

    def all(self) -> list:
        return self._messages

    def last(self) -> dict:
        return self._messages[-1]

    def get_conversation(self, limit: int = 1) -> str:
        return "\n".join(
            [
                f"{'User' if message['is_user'] else 'Bot'}: {message['message']}"
                for message in self._messages[-limit:]
            ]
        )

    def clear(self):
        self._messages = []
