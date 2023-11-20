from pydantic import BaseModel, validator, Field
from typing import Optional, List, Any, Dict, TypedDict
from pandasai.constants import DEFAULT_CHART_DIRECTORY
from ..llm import LLM, LangchainLLM
from ..exceptions import LLMNotFoundError
from ..helpers.viz_library_types.base import VisualizationLibrary


class LogServerConfig(TypedDict):
    server_url: str
    api_key: str


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    use_error_correction_framework: bool = True
    custom_prompts: Dict = Field(default_factory=dict)
    custom_instructions: Optional[str] = None
    open_charts: bool = True
    save_charts: bool = False
    save_charts_path: str = DEFAULT_CHART_DIRECTORY
    custom_whitelisted_dependencies: List[str] = Field(default_factory=list)
    max_retries: int = 3
    lazy_load_connector: bool = True
    response_parser: Any = None
    llm: Any = None
    data_viz_library: Optional[VisualizationLibrary] = None
    log_server: LogServerConfig = None
    direct_sql: bool = False

    class Config:
        arbitrary_types_allowed = True

    @validator("llm")
    def validate_llm(cls, llm):
        if llm is None or not isinstance(llm, LLM or LangchainLLM):
            raise LLMNotFoundError("LLM is required")
        return llm
