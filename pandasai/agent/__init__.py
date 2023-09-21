import json
from typing import Union, List, Optional
from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.logger import Logger
from pandasai.helpers.memory import Memory
from pandasai.prompts.clarification_questions_prompt import ClarificationQuestionPrompt
from pandasai.schemas.df_config import Config

from pandasai.smart_datalake import SmartDatalake


class Agent:
    """
    Agent class to improve the conversational experience in PandasAI
    """

    _memory: Memory
    _lake: SmartDatalake = None
    logger: Logger = None

    def __init__(
        self,
        dfs: Union[DataFrameType, List[DataFrameType]],
        config: Optional[Union[Config, dict]] = None,
        logger: Logger = None,
        memory_size=1,
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
        self._memory = Memory(memory_size * 2)

    def _get_conversation(self):
        """
        Get Conversation from history

        """
        return "\n".join(
            [
                f"{'User ' if message['is_user'] else 'Answers'}: "
                f"{message['message']}"
                for i, message in enumerate(self._memory.all())
            ]
        )

    def chat(self, query: str):
        """
        Simulate a chat interaction with the assistant on Dataframe.
        """
        self._memory.add(query, True)
        conversation = self._get_conversation()
        result = self._lake.chat(query, conversation)
        self._memory.add(result, False)
        return result

    def _get_clarification_prompt(self):
        """
        Create a clarification prompt with relevant variables.
        """
        prompt = ClarificationQuestionPrompt()
        prompt.set_var("dfs", self._lake.dfs)
        prompt.set_var("conversation", self._get_conversation())
        return prompt

    def clarification_questions(self):
        """
        Generate and return up to three clarification questions based on a given prompt.
        """
        try:
            prompt = self._get_clarification_prompt()
            result = self._lake.llm.generate_code(prompt)
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your clarification questions, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )
        questions = json.loads(result)
        return questions[:3]

    def start_new_conversation(self):
        """
        Clears the previous conversation
        """
        self._memory.clear()
