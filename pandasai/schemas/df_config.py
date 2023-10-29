from pydantic import BaseModel, validator, Field
from typing import Optional, List, Any, Dict, Type, TypedDict

from pandasai.responses import ResponseParser
from ..middlewares.base import Middleware
from ..callbacks.base import BaseCallback
from ..llm import LLM, LangchainLLM
from ..exceptions import LLMNotFoundError


class LogServerConfig(TypedDict):
    server_url: str
    api_key: str


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    use_error_correction_framework: bool = True
    use_advanced_reasoning_framework: bool = False
    custom_prompts: Dict = Field(default_factory=dict)
    custom_instructions: Optional[str] = None
    open_charts: bool = True
    save_charts: bool = False
    save_charts_path: str = "exports/charts"
    custom_whitelisted_dependencies: List[str] = Field(default_factory=list)
    max_retries: int = 3
    middlewares: List[Middleware] = Field(default_factory=list)
    callback: Optional[BaseCallback] = None
    lazy_load_connector: bool = True
    response_parser: Type[ResponseParser] = None
    llm: Any = None
    log_server: LogServerConfig = None
    visualization_library : str = "matplotlib"

    class Config:
        arbitrary_types_allowed = True

    @validator("llm")
    def validate_llm(cls, llm):
        if llm is None or not isinstance(llm, LLM or LangchainLLM):
            raise LLMNotFoundError("LLM is required")
        return llm
