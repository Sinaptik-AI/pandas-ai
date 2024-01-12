import uuid
from pandasai.helpers.output_types._output_types import BaseOutputType


class SmartDatalakePipelineInput:
    query: str
    output_type: BaseOutputType
    instance: str
    conversation_id: uuid.UUID
    prompt_id: uuid.UUID
    is_related_query: bool

    def __init__(
        self,
        query: str,
        output_type: str,
        instance: str,
        conversation_id: uuid.UUID,
        prompt_id: uuid.UUID,
        is_related_query: bool,
    ) -> None:
        self.query = query
        self.output_type = output_type
        self.instance = instance
        self.conversation_id = conversation_id
        self.prompt_id = prompt_id
        self.is_related_query = is_related_query
