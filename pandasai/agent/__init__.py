import json
from typing import Union, List, Optional
from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.logger import Logger
from pandasai.helpers.memory import Memory
from pandasai.prompts.base import AbstractPrompt
from pandasai.prompts.clarification_questions_prompt import ClarificationQuestionPrompt
from pandasai.prompts.explain_prompt import ExplainPrompt
from pandasai.prompts.rephase_query_prompt import RephraseQueryPrompt
from pandasai.schemas.df_config import Config
from pandasai.smart_datalake import SmartDatalake


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
        memory_size: int = 1,
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
        self._logger = self._lake.logger

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
            result = self._lake.chat(query, output_type=output_type)
            return result
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

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
                f"""Explaination:  {response}
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
