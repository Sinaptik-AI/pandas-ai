import json
from typing import Union, List, Optional

from ..helpers.df_info import DataFrameType
from ..helpers.logger import Logger
from ..helpers.memory import Memory
from ..prompts.base import AbstractPrompt
from ..prompts.clarification_questions_prompt import ClarificationQuestionPrompt
from ..prompts.explain_prompt import ExplainPrompt
from ..prompts.rephase_query_prompt import RephraseQueryPrompt
from ..prompts.check_if_relevant_to_conversation import (
    CheckIfRelevantToConversationPrompt,
)
from ..schemas.df_config import Config
from ..skills import Skill
from ..smart_datalake import SmartDatalake


class Agent:
    """
    Agent class to improve the conversational experience in PandasAI
    """

    _lake: SmartDatalake = None
    _logger: Optional[Logger] = None

    def __init__(
        self,
        dfs: Union[DataFrameType, List[DataFrameType]],
        config: Optional[Union[Config, dict]] = None,
        logger: Optional[Logger] = None,
        memory_size: int = 10,
    ):
        """
        Args:
            df (Union[DataFrameType, List[DataFrameType]]): DataFrame can be Pandas,
            Polars or Database connectors
            memory_size (int, optional): Conversation history to use during chat.
            Defaults to 1.
        """

        if not isinstance(dfs, list):
            dfs = [dfs]

        self._lake = SmartDatalake(dfs, config, logger, memory=Memory(memory_size))

        # set instance type in SmartDataLake
        self._lake.set_instance_type(self.__class__.__name__)

        self._logger = self._lake.logger

    def add_skills(self, *skills: Skill):
        """
        Add Skills to PandasAI
        """
        self._lake.add_skills(*skills)

    def _call_llm_with_prompt(self, prompt: AbstractPrompt):
        """
        Call LLM with prompt using error handling to retry based on config
        Args:
            prompt (AbstractPrompt): AbstractPrompt to pass to LLM's
        """
        retry_count = 0
        while retry_count < self._lake.config.max_retries:
            try:
                result: str = self._lake.llm.call(prompt)
                if prompt.validate(result):
                    return result
                else:
                    raise Exception("Response validation failed!")
            except Exception:
                if (
                    not self._lake.use_error_correction_framework
                    or retry_count >= self._lake.config.max_retries - 1
                ):
                    raise
                retry_count += 1

    def chat(self, query: str, output_type: Optional[str] = None):
        """
        Simulate a chat interaction with the assistant on Dataframe.
        """
        try:
            is_related = self.check_if_related_to_conversation(query)
            self._lake.is_related_query(is_related)
            return self._lake.chat(query, output_type=output_type)
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def add_message(self, message, is_user=False):
        """
        Add message to the memory. This is useful when you want to add a message
        to the memory without calling the chat function (for example, when you
        need to add a message from the agent).
        """
        self._lake._memory.add(message, is_user=is_user)

    def check_if_related_to_conversation(self, query: str) -> bool:
        """
        Check if the query is related to the previous conversation
        """
        if self._lake._memory.count() == 0:
            return

        prompt = CheckIfRelevantToConversationPrompt(
            conversation=self._lake._memory.get_conversation(),
            query=query,
        )

        result = self._call_llm_with_prompt(prompt)

        related = "true" in result
        self._logger.log(
            f"""Check if the new message is related to the conversation: {related}"""
        )

        if not related:
            self._lake.clear_memory()

        return related

    def clarification_questions(self, query: str) -> List[str]:
        """
        Generate clarification questions based on the data
        """
        prompt = ClarificationQuestionPrompt(
            dataframes=self._lake.dfs,
            conversation=self._lake._memory.get_conversation(),
            query=query,
        )

        result = self._call_llm_with_prompt(prompt)
        self._logger.log(
            f"""Clarification Questions:  {result}
            """
        )
        result = result.replace("```json", "").replace("```", "")
        questions: list[str] = json.loads(result)
        return questions[:3]

    def start_new_conversation(self):
        """
        Clears the previous conversation
        """
        self._lake.clear_memory()

    def explain(self) -> str:
        """
        Returns the explanation of the code how it reached to the solution
        """
        try:
            prompt = ExplainPrompt(
                conversation=self._lake._memory.get_conversation(),
                code=self._lake.last_code_executed,
            )
            response = self._call_llm_with_prompt(prompt)
            self._logger.log(
                f"""Explanation:  {response}
                """
            )
            return response
        except Exception as exception:
            return (
                "Unfortunately, I was not able to explain, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def rephrase_query(self, query: str):
        try:
            prompt = RephraseQueryPrompt(
                query=query,
                dataframes=self._lake.dfs,
                conversation=self._lake._memory.get_conversation(),
            )
            response = self._call_llm_with_prompt(prompt)
            self._logger.log(
                f"""Rephrased Response:  {response}
                """
            )
            return response
        except Exception as exception:
            return (
                "Unfortunately, I was not able to repharse query, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    @property
    def last_code_generated(self):
        return self._lake.last_code_generated

    @property
    def last_code_executed(self):
        return self._lake.last_code_executed

    @property
    def last_prompt(self):
        return self._lake.last_prompt

    @property
    def last_query_log_id(self):
        return self._lake.last_query_log_id
