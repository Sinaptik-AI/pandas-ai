from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pandasai.helpers.cache import Cache
from pandasai.helpers.logger import Logger
from pandasai.helpers.memory import Memory

from pandasai.config import Config
from pandasai.vectorstores.vectorstore import VectorStore

if TYPE_CHECKING:
    from pandasai.dataframe import DataFrame
    from pandasai.dataframe import VirtualDataFrame
    from pandasai.llm.base import LLM


@dataclass
class AgentState:
    """
    Context class for managing pipeline attributes and passing them between steps.
    """

    dfs: List[Union[DataFrame, VirtualDataFrame]] = field(default_factory=list)
    config: Union[Config, dict] = field(default_factory=dict)
    memory: Memory = field(default_factory=Memory)
    cache: Optional[Cache] = None
    llm: LLM = None
    vectorstore: Optional[VectorStore] = None
    intermediate_values: Dict[str, Any] = field(default_factory=dict)
    logger: Optional[Logger] = None
    last_code_generated: Optional[str] = None
    last_code_executed: Optional[str] = None
    last_prompt_id: str = None
    last_prompt_used: str = None
    output_type: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.config, dict):
            self.config = Config(**self.config)

        # Initialize cache only if enabled in config
        if getattr(self.config, "enable_cache", False) and self.cache is None:
            self.cache = Cache()

    def reset_intermediate_values(self):
        """Resets the intermediate values dictionary."""
        self.intermediate_values.clear()

    def add(self, key: str, value: Any):
        """Adds a single key-value pair to intermediate values."""
        self.intermediate_values[key] = value

    def add_many(self, values: Dict[str, Any]):
        """Adds multiple key-value pairs to intermediate values."""
        self.intermediate_values.update(values)

    def get(self, key: str, default: Any = "") -> Any:
        """Fetches a value from intermediate values or returns a default."""
        return self.intermediate_values.get(key, default)
