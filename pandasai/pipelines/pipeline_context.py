from typing import Any, List, Union
from pandasai.helpers.cache import Cache

from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.memory import Memory
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.schemas.df_config import Config
from pandasai.smart_dataframe import SmartDataframe


class PipelineContext:
    """
    Pass Context to the pipeline which is accessible to each step via kwargs
    """

    _dfs: List[Union[DataFrameType, SmartDataframe]]
    _memory: Memory
    _skills: SkillsManager
_cache: Cache

    def __init__(
        self,
        dfs: List[Union[DataFrameType, SmartDataframe]],
        config: Config,
        memory: Memory = None,
        skills: SkillsManager = None,
        cache: Cache = None,
    ) -> None:
        self._dfs = self._load_dfs(dfs, config)
        self._memory = memory if memory is not None else Memory()
        self._skills = skills if skills is not None else SkillsManager()
        self._cache = cache if cache is not None else Cache()

    def _load_dfs(self, dfs: List[Union[DataFrameType, Any]], config: Config):
        """
        Load all the dataframes to be used in the smart datalake.

        Args:
            dfs (List[Union[DataFrameType, Any]]): List of dataframes to be used
        """

        from ..smart_dataframe import SmartDataframe

        smart_dfs = []
        for df in dfs:
            if not isinstance(df, SmartDataframe):
                smart_dfs.append(SmartDataframe(df, config=config))
            else:
                smart_dfs.append(df)

        return smart_dfs

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
