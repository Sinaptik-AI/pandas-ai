from typing import List, Optional, Union
from pandasai.helpers.cache import Cache

from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.memory import Memory
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.schemas.df_config import Config
from pandasai.smart_dataframe import SmartDataframe, load_smartdataframes


class PipelineContext:
    """
    Pass Context to the pipeline which is accessible to each step via kwargs
    """

    _dfs: List[Union[DataFrameType, SmartDataframe]]
    _memory: Memory
    _skills: SkillsManager
    _cache: Cache
    _config: Config

    def __init__(
        self,
        dfs: List[Union[DataFrameType, SmartDataframe]],
        config: Optional[Union[Config, dict]] = None,
        memory: Memory = None,
        skills: SkillsManager = None,
        cache: Cache = None,
    ) -> None:
        if isinstance(config, dict):
            config = Config(**config)

        self._dfs = load_smartdataframes(dfs, config)
        self._memory = memory if memory is not None else Memory()
        self._skills = skills if skills is not None else SkillsManager()
        self._cache = cache if cache is not None else Cache()
        self._config = config

    @property
    def dfs(self) -> List[Union[DataFrameType, SmartDataframe]]:
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
