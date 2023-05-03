""" PandasAI is a wrapper around a LLM to make dataframes convesational """
import io
import sys
import pandas as pd
from .llm.base import LLM
from .helpers.notebook import Notebook
from .exceptions import LLMNotFoundError


class PandasAI:
    """PandasAI is a wrapper around a LLM to make dataframes convesational"""

    _task_instruction: str = """
There is a dataframe in pandas (python).
The name of the dataframe is `df`.
This is the result of `print(df.head({rows_to_display}))`:
{df_head}.

Return the python code (do not import anything) and make sure to prefix the python code with <startCode> exactly and suffix the code with <endCode> exactly 
to get the answer to the following question :
"""
    _response_instruction: str = """
Question: {question}
Answer: {answer}

Rewrite the answer to the question in a conversational way.
"""

    _error_correct_instruction: str = """
    For the task defined below:
    {orig_task}
    you generated this python code:
    {code}
    and this fails with the following error:
    {error_returned}
    Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error.
    Make sure to prefix the python code with <startCode> exactly and suffix the code with <endCode> exactly.
    """
    _llm: LLM
    _verbose: bool = False
    _is_conversational_answer: bool = True
    _enforce_privacy: bool = False
    _max_retries: int = 3
    _original_instruction_and_prompt = None
    _is_notebook: bool = False
    last_code_generated: str = None
    code_output: str = None

    def __init__(
        self,
        llm=None,
        conversational=True,
        verbose=False,
        enforce_privacy=False,
    ):
        if llm is None:
            raise LLMNotFoundError(
                "An LLM should be provided to instantiate a PandasAI instance"
            )
        self._llm = llm
        self._is_conversational_answer = conversational
        self._verbose = verbose
        self._enforce_privacy = enforce_privacy

        self.notebook = Notebook()
        self._in_notebook = self.notebook.in_notebook()

    def conversational_answer(self, question: str, code: str, answer: str) -> str:
        """Return the conversational answer"""
        if self._enforce_privacy:
            # we don't want to send potentially sensitive data to the LLM server
            # if the user has set enforce_privacy to True
            return answer

        instruction = self._response_instruction.format(
            question=question, code=code, answer=answer
        )
        return self._llm.call(instruction, "")

    def run(
        self,
        data_frame: pd.DataFrame,
        prompt: str,
        is_conversational_answer: bool = None,
        show_code: bool = False,
    ) -> str:
        """Run the LLM with the given prompt"""
        self.log(f"Running PandasAI with {self._llm.type} LLM...")

        rows_to_display = 5
        if self._enforce_privacy:
            rows_to_display = 0

        code = self._llm.generate_code(
            self._task_instruction.format(
                df_head=data_frame.head(rows_to_display),
                rows_to_display=rows_to_display,
            ),
            prompt,
        )
        self._original_instruction_and_prompt = (
            self._task_instruction.format(
                df_head=data_frame.head(rows_to_display),
                rows_to_display=rows_to_display,
            )
            + prompt
        )
        self.last_code_generated = code
        self.log(
            f"""
Code generated:
```
{code}
```"""
        )
        if show_code and self._in_notebook:
            self.notebook.create_new_cell(code)

        answer = self.run_code(code, data_frame, False)
        self.code_output = answer
        self.log(f"Answer: {answer}")

        if is_conversational_answer is None:
            is_conversational_answer = self._is_conversational_answer
        if is_conversational_answer:
            answer = self.conversational_answer(prompt, code, answer)
            self.log(f"Conversational answer: {answer}")
        return answer

    def run_code(
        self,
        code: str,
        df: pd.DataFrame,  # pylint: disable=W0613 disable=C0103
        use_error_correction_framework: bool = False,
    ) -> str:
        # pylint: disable=W0122 disable=W0123 disable=W0702:bare-except
        """Run the code in the current context and return the result"""

        # Redirect standard output to a StringIO buffer
        output = io.StringIO()
        sys.stdout = output

        # Execute the code
        if use_error_correction_framework:
            count = 0
            code_to_run = code
            while count < self._max_retries:
                try:
                    exec(code_to_run)
                    code = code_to_run
                    break
                except Exception as e:  # pylint: disable=W0718 disable=C0103
                    count += 1
                    error_correcting_instruction = (
                        self._error_correct_instruction.format(
                            orig_task=self._original_instruction_and_prompt,
                            code=code,
                            error_returned=e,
                        )
                    )
                    code_to_run = self._llm.generate_code(
                        error_correcting_instruction, ""
                    )
        else:
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
