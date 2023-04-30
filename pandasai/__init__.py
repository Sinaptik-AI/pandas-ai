""" PandasAI is a wrapper around a LLM to make dataframes convesational """
import io
import sys
import pandas as pd
from .llm.base import LLM
from .exceptions import LLMNotFoundError


class PandasAI:
    """PandasAI is a wrapper around a LLM to make dataframes convesational"""

    _task_instruction: str = """
There is a dataframe in pandas (python).
The name of the dataframe is `df`.
This is the result of `print(df.head())`:
{df_head}.

Return the python code (do not import anything) to get the answer to the following question:
"""
    _response_instruction: str = """
Question: {question}
Answer: {answer}

Rewrite the answer to the question in a conversational way.
"""
    _llm: LLM
    _verbose: bool = False
    _is_conversational_answer: bool = True
    last_code_generated: str = None
    code_output: str = None

    def __init__(self, llm=None, conversational=True, verbose=False):
        if llm is None:
            raise LLMNotFoundError(
                "An LLM should be provided to instantiate a PandasAI instance"
            )
        self._llm = llm
        self._is_conversational_answer = conversational
        self._verbose = verbose

    def conversational_answer(self, question: str, code: str, answer: str) -> str:
        """Return the conversational answer"""
        instruction = self._response_instruction.format(
            question=question, code=code, answer=answer
        )
        return self._llm.call(instruction, answer)

    def run(
        self,
        data_frame: pd.DataFrame,
        prompt: str,
        is_conversational_answer: bool = None,
    ) -> str:
        """Run the LLM with the given prompt"""
        self.log(f"Running PandasAI with {self._llm.type} LLM...")

        code = self._llm.generate_code(
            self._task_instruction.format(df_head=data_frame.head()), prompt
        )
        self.last_code_generated = code
        self.log(
            f"""
Code generated:
```
{code}
```"""
        )

        answer = self.run_code(code, data_frame)
        self.code_output = answer
        self.log(f"Answer: {answer}")

        if is_conversational_answer is None:
            is_conversational_answer = self._is_conversational_answer
        if is_conversational_answer:
            answer = self.conversational_answer(prompt, code, answer)
            self.log(f"Conversational answer: {answer}")
        return answer

    def run_code(
        self, code: str, df: pd.DataFrame  # pylint: disable=W0613 disable=C0103
    ) -> str:
        # pylint: disable=W0122 disable=W0123 disable=W0702:bare-except
        """Run the code in the current context and return the result"""

        # Redirect standard output to a StringIO buffer
        output = io.StringIO()
        sys.stdout = output

        # Execute the code
        exec(code)

        # Restore standard output and get the captured output
        sys.stdout = sys.__stdout__
        captured_output = output.getvalue()

        # Evaluate the last line and return its value or the captured output
        lines = code.strip().split("\n")
        last_line = lines[-1].strip()
        if last_line.startswith("print(") and last_line.endswith(")"):
            # Last line is already printing
            return eval(last_line[6:-1])
        # Evaluate last line and return its value or the captured output
        try:
            result = eval(last_line)
            return result
        except:
            return captured_output

    def log(self, message: str):
        """Log a message"""
        if self._verbose:
            print(message)
