from pydantic import BaseModel
from typing import Union, List, Optional
from ..middlewares.base import Middleware
from ..llm.base import LLM
from ..llm.langchain import LangchainLLM
from ..callbacks.base import BaseCallback


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    anonymize_dataframe: bool = True
    use_error_correction_framework: bool = True
    custom_prompts: dict = {}
    save_charts: bool = False
    save_charts_path: str = "exports/charts"
    custom_whitelisted_dependencies: List[str] = []
    max_retries: int = 3
    middlewares: List[Middleware] = []
    callback: Optional[BaseCallback] = None
    llm: Union[LLM, LangchainLLM] = None

    class Config:
        arbitrary_types_allowed = True
