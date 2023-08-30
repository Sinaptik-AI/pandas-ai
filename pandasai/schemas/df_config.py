from pydantic import BaseModel, validator
from typing import List, Optional, Any
from ..middlewares.base import Middleware
from ..callbacks.base import BaseCallback
from ..llm import LLM, LangchainLLM
from ..exceptions import LLMNotFoundError


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    use_error_correction_framework: bool = True
    custom_prompts: dict = {}
    save_charts: bool = False
    save_charts_path: str = "exports/charts"
    custom_whitelisted_dependencies: List[str] = []
    max_retries: int = 3
    middlewares: List[Middleware] = []
    callback: Optional[BaseCallback] = None
    llm: Any = None

    class Config:
        arbitrary_types_allowed = True

    @validator("llm")
    def validate_llm(cls, llm):
        if llm is None or not isinstance(llm, LLM or LangchainLLM):
            raise LLMNotFoundError("LLM is required")
        return llm
