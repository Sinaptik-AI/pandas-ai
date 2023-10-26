from typing import List, Union

from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.memory import Memory
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.smart_dataframe import SmartDataframe


class PipelineContext:
    """
    Pass Context to the pipeline which is accessible to each step via kwargs
    """

    _dfs: List[Union[DataFrameType, SmartDataframe]]
    _memory: Memory
    _skills: SkillsManager

    def __init__(
        self,
        dfs: List[Union[DataFrameType, SmartDataframe]],
        memory: Memory = None,
        skills: SkillsManager = None,
    ) -> None:
        self._dfs = dfs
        self._memory = memory if memory is not None else Memory()
        self._skills = skills if skills is not None else SkillsManager()

    @property
    def dfs(self) -> List[Union[DataFrameType, SmartDataframe]]:
        return self._dfs

    @property
    def memory(self):
        return self._memory

    @property
    def skills(self):
        return self._skills
