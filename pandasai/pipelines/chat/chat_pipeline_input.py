import uuid
from dataclasses import dataclass


@dataclass
class ChatPipelineInput:
    """
    Contain all the data needed by the chat pipeline
    """

    query: str
    output_type: str
    instance: str
    conversation_id: uuid.UUID
    prompt_id: uuid.UUID

    def __init__(
        self,
        query: str,
        output_type: str,
        conversation_id: uuid.UUID,
        prompt_id: uuid.UUID,
    ) -> None:
        self.query = query
        self.output_type = output_type
        self.conversation_id = conversation_id
        self.prompt_id = prompt_id
