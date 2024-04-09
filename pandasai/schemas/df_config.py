from typing import Any, List, Optional, TypedDict

from pandasai.constants import DEFAULT_CHART_DIRECTORY
from pandasai.helpers.dataframe_serializer import DataframeSerializerType
from pandasai.pydantic import BaseModel, Field, validator

from ..llm import LLM, BambooLLM, LangchainLLM


class LogServerConfig(TypedDict):
    server_url: str
    api_key: str


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    use_error_correction_framework: bool = True
    open_charts: bool = True
    save_charts: bool = False
    save_charts_path: str = DEFAULT_CHART_DIRECTORY
    custom_whitelisted_dependencies: List[str] = Field(default_factory=list)
    max_retries: int = 3
    lazy_load_connector: bool = True
    response_parser: Any = None
    llm: LLM = None
    data_viz_library: Optional[str] = ""
    log_server: LogServerConfig = None
    direct_sql: bool = False
    dataframe_serializer: DataframeSerializerType = DataframeSerializerType.CSV

    class Config:
        arbitrary_types_allowed = True

    @validator("llm", always=True)
    def validate_llm(cls, llm) -> LLM:
        if not isinstance(llm, (LLM, LangchainLLM)):  # also covers llm is None
            return BambooLLM()
        return llm
