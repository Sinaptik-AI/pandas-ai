import ast

from ..code import check_malicious_keywords_in_code
from ..exceptions import MaliciousCodeError
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

    def before_code_execution(self, code: str):
        """
        A method to be called after code execution.

        Args:
            code (str): A python code
        """
        malicious, badblock = check_malicious_keywords_in_code(code)
        if malicious:
            raise MaliciousCodeError(
                "The generated code contains references to io or os modules or b64decode method which can be used to execute or access system resources in unsafe ways: "
                + ast.unparse(badblock)
            )

        self.agent.last_code_executed = code

    def on_result(self, result):
        """
        A method to be called after code execution.

        Args:
            result (Any): A python code
        """
        self.agent.last_result = result
