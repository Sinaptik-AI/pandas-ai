import json
from typing import Union, List, Optional
from pandasai.agent.response import ClarificationResponse
from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.logger import Logger
from pandasai.helpers.memory import Memory
from pandasai.prompts.base import Prompt
from pandasai.prompts.clarification_questions_prompt import ClarificationQuestionPrompt
from pandasai.prompts.explain_prompt import ExplainPrompt
from pandasai.schemas.df_config import Config

from pandasai.smart_datalake import SmartDatalake


class Agent:
    """
    Agent class to improve the conversational experience in PandasAI
    """

    _memory: Memory
    _lake: SmartDatalake = None
    logger: Optional[Logger] = None

    def __init__(
        self,
        dfs: Union[DataFrameType, List[DataFrameType]],
        config: Optional[Union[Config, dict]] = None,
        logger: Optional[Logger] = None,
        memory_size: int = 1,
    ):
        """
        Args:
            df (Union[SmartDataframe, SmartDatalake]): _description_
            memory_size (int, optional): _description_. Defaults to 1.
        """

        if not isinstance(dfs, list):
            dfs = [dfs]

        self._lake = SmartDatalake(dfs, config, logger)
        self.logger = self._lake.logger
        # For the conversation multiple the memory size by 2
        self._memory = Memory(memory_size * 2)

    def _get_conversation(self):
        """
        Get Conversation from history

        """
        return "\n".join(
            [
                f"{'Question' if message['is_user'] else 'Answer'}: "
                f"{message['message']}"
                for i, message in enumerate(self._memory.all())
            ]
        )

    def chat(self, query: str, output_type: Optional[str] = None):
        """
        Simulate a chat interaction with the assistant on Dataframe.
        """
        try:
            self._memory.add(query, True)
            conversation = self._get_conversation()
            result = self._lake.chat(
                query, output_type=output_type, start_conversation=conversation
            )
            self._memory.add(result, False)
            return result
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def _get_clarification_prompt(self) -> Prompt:
        """
        Create a clarification prompt with relevant variables.
        """
        prompt = ClarificationQuestionPrompt()
        prompt.set_var("dfs", self._lake.dfs)
        prompt.set_var("conversation", self._get_conversation())
        return prompt

    def clarification_questions(self) -> ClarificationResponse:
        """
        Generate clarification questions based on the data
        """
        try:
            prompt = self._get_clarification_prompt()
            result = self._lake.llm.call(prompt)
            self.logger.log(
                f"""Clarification Questions:  {result}
                """
            )
            questions: list[str] = json.loads(result)
            return ClarificationResponse(
                success=True, questions=questions[:3], message=result
            )
        except Exception as exception:
            return ClarificationResponse(
                False,
                [],
                "Unfortunately, I was not able to get your clarification questions, "
                "because of the following error:\n"
                f"\n{exception}\n",
            )

    def start_new_conversation(self):
        """
        Clears the previous conversation
        """

        self._memory.clear()

    def explain(self) -> str:
        """
        Returns the explanation of the code how it reached to the solution
        """
        try:
            prompt = ExplainPrompt()
            prompt.set_var("code", self._lake.last_code_executed)
            prompt.set_var("conversation", self._get_conversation())
            response = self._lake.llm.call(prompt)
            self.logger.log(
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
