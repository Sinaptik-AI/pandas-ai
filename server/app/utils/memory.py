from typing import List

from pandasai.helpers.memory import Memory
from app.models import ConversationMessage


def prepare_conv_memory(messages: List[ConversationMessage]) -> Memory:
    memory = Memory()
    for message in messages:
        if message.response:
            memory.add(message.query, is_user=True)
            if message.code_generated:
                memory.add(f"```python\n{message.code_generated}\n```", is_user=False)
            else:
                memory.add(
                    "\n".join([str(item["message"]) for item in message.response]),
                    is_user=False,
                )

    return memory
