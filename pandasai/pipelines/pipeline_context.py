from typing import List, Optional, Union, Any
from pandasai.helpers.cache import Cache

from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.memory import Memory
from pandasai.helpers.query_exec_tracker import QueryExecTracker
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.schemas.df_config import Config


class PipelineContext:
    """
    Pass Context to the pipeline which is accessible to each step via kwargs
    """

    _dfs: List[Union[DataFrameType, Any]]
    _memory: Memory
    _skills: SkillsManager
    _cache: Optional[Cache]
    _config: Config
    _query_exec_tracker: QueryExecTracker
    _intermediate_values: dict

    def __init__(
        self,
        dfs: List[Union[DataFrameType, Any]],
        config: Optional[Union[Config, dict]] = None,
        memory: Optional[Memory] = None,
        skills: Optional[SkillsManager] = None,
        cache: Optional[Cache] = None,
        query_exec_tracker: Optional[QueryExecTracker] = None,
    ) -> None:
        from pandasai.smart_dataframe import load_smartdataframes

        if isinstance(config, dict):
            config = Config(**config)

        self._dfs = load_smartdataframes(dfs, config)
        self._memory = memory if memory is not None else Memory()
        self._skills = skills if skills is not None else SkillsManager()
        if config.enable_cache:
            self._cache = cache if cache is not None else Cache()
        else:
            self._cache = None
        self._config = config
        self._query_exec_tracker = query_exec_tracker
        self._intermediate_values = {}

    @property
    def dfs(self) -> List[Union[DataFrameType, Any]]:
        return self._dfs

    @property
    def memory(self):
        return self._memory

    @property
    def skills(self):
        return self._skills

    @property
    def cache(self):
        return self._cache

    @property
    def config(self):
        return self._config

    @property
    def query_exec_tracker(self):
        return self._query_exec_tracker

    def add_intermediate_value(self, key: str, value: Any):
        self._intermediate_values[key] = value

    def get_intermediate_value(self, key: str):
        return self._intermediate_values.get(key, "")
