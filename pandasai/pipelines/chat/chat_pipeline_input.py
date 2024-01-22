from dataclasses import dataclass
import uuid


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
    is_related_query: bool

    def __init__(
        self,
        query: str,
        output_type: str,
        conversation_id: uuid.UUID,
        prompt_id: uuid.UUID,
        is_related_query: bool,
    ) -> None:
        self.query = query
        self.output_type = output_type
        self.conversation_id = conversation_id
        self.prompt_id = prompt_id
        self.is_related_query = is_related_query
