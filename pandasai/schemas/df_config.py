from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict

from pandasai.constants import DEFAULT_CHART_DIRECTORY
from pandasai.helpers.dataframe_serializer import DataframeSerializerType

from ..llm import LLM, BambooLLM
from importlib.util import find_spec


class LogServerConfig(BaseModel):
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
    response_parser: Any = None
    llm: LLM = Field(
        default_factory=lambda: BambooLLM(
            api_key="dummy_key_for_testing", endpoint_url=None
        )
    )
    data_viz_library: Optional[str] = ""
    log_server: Optional[LogServerConfig] = None
    direct_sql: bool = False
    dataframe_serializer: DataframeSerializerType = DataframeSerializerType.CSV

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("llm", mode="before")
    @classmethod
    def validate_llm(cls, v: Any) -> LLM:
        if v is None:
            return BambooLLM(api_key="dummy_key_for_testing", endpoint_url=None)
        if find_spec("pandasai_langchain") is not None:
            from pandasai_langchain.langchain import LangchainLLM

            if not isinstance(v, (LLM, LangchainLLM)):
                return BambooLLM(api_key="dummy_key_for_testing", endpoint_url=None)
        elif not isinstance(v, LLM):
            return BambooLLM(api_key="dummy_key_for_testing", endpoint_url=None)
        return v

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Config":
        return cls(**config)
