from ..prompts import BasePrompt


class Callbacks:
    def __init__(self, agent):
        self.agent = agent

    def on_prompt_generation(self, prompt: BasePrompt) -> str:
        """
        A method to be called after prompt generation.

        Args:
            prompt (str): A prompt
        """
        self.agent.last_prompt = str(prompt)

    def on_code_generation(self, code: str):
        """
        A method to be called after code generation.

        Args:
            code (str): A python code
        """
        self.agent.last_code_generated = code

    def on_code_execution(self, code: str):
        """
        A method to be called after code execution.

        Args:
            code (str): A python code
        """
        self.agent.last_code_executed = self.agent.context.get("last_code_executed")

    def on_result(self, result):
        """
        A method to be called after code execution.

        Args:
            result (Any): A python code
        """
        self.agent.last_result = result
