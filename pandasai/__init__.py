""" PandasAI is a wrapper around a LLM to make dataframes convesational """
import ast
import io
import re
from contextlib import redirect_stdout
from typing import Optional

import astor
import matplotlib.pyplot as plt
import pandas as pd

from .constants import WHITELISTED_BUILTINS, WHITELISTED_LIBRARIES
from .exceptions import LLMNotFoundError
from .helpers.anonymizer import anonymize_dataframe_head
from .helpers.notebook import Notebook
from .llm.base import LLM
from .prompts.correct_error_prompt import CorrectErrorPrompt
from .prompts.generate_python_code import GeneratePythonCodePrompt
from .prompts.generate_response import GenerateResponsePrompt


# pylint: disable=too-many-instance-attributes disable=too-many-arguments
class PandasAI:
    """PandasAI is a wrapper around a LLM to make dataframes conversational"""

    _llm: LLM
    _verbose: bool = False
    _is_conversational_answer: bool = True
    _enforce_privacy: bool = False
    _max_retries: int = 3
    _is_notebook: bool = False
    _original_instructions: dict = {
        "question": None,
        "df_head": None,
        "num_rows": None,
        "num_columns": None,
        "rows_to_display": None,
    }
    last_code_generated: Optional[str] = None
    last_run_code: Optional[str] = None
    code_output: Optional[str] = None
    last_error: Optional[str] = None

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

    def conversational_answer(self, question: str, answer: str) -> str:
        """Return the conversational answer"""
        if self._enforce_privacy:
            # we don't want to send potentially sensitive data to the LLM server
            # if the user has set enforce_privacy to True
            return answer

        instruction = GenerateResponsePrompt(question=question, answer=answer)
        return self._llm.call(instruction, "")

    def run(
        self,
        data_frame: pd.DataFrame,
        prompt: str,
        is_conversational_answer: bool = None,
        show_code: bool = False,
        anonymize_df: bool = True,
        use_error_correction_framework: bool = True,
    ) -> str:
        """Run the LLM with the given prompt"""
        self.log(f"Running PandasAI with {self._llm.type} LLM...")

        try:
            rows_to_display = 0 if self._enforce_privacy else 5

            df_head = data_frame.head(rows_to_display)
            if anonymize_df:
                df_head = anonymize_dataframe_head(df_head)

            code = self._llm.generate_code(
                GeneratePythonCodePrompt(
                    prompt=prompt,
                    df_head=df_head,
                    num_rows=data_frame.shape[0],
                    num_columns=data_frame.shape[1],
                    rows_to_display=rows_to_display,
                ),
                prompt,
            )
            self._original_instructions = {
                "question": prompt,
                "df_head": df_head,
                "num_rows": data_frame.shape[0],
                "num_columns": data_frame.shape[1],
                "rows_to_display": rows_to_display,
            }
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

            answer = self.run_code(
                code,
                data_frame,
                use_error_correction_framework=use_error_correction_framework,
            )
            self.code_output = answer
            self.log(f"Answer: {answer}")

            if is_conversational_answer is None:
                is_conversational_answer = self._is_conversational_answer
            if is_conversational_answer:
                answer = self.conversational_answer(prompt, answer)
                self.log(f"Conversational answer: {answer}")
            return answer
        except Exception as exception:  # pylint: disable=broad-except
            self.last_error = str(exception)
            return (
                "Unfortunately, I was not able to answer your question. "
                "Please try again. If the problem persists, try rephrasing your question."
            )

    def __call__(
        self,
        data_frame: pd.DataFrame,
        prompt: str,
        is_conversational_answer: bool = None,
        show_code: bool = False,
        anonymize_df: bool = True,
        use_error_correction_framework: bool = True,
    ) -> str:
        """Run the LLM with the given prompt"""
        return self.run(
            data_frame,
            prompt,
            is_conversational_answer,
            show_code,
            anonymize_df,
            use_error_correction_framework,
        )

    def is_unsafe_import(self, node: ast.stmt) -> bool:
        """Remove non-whitelisted imports from the code to prevent malicious code execution"""

        return isinstance(node, (ast.Import, ast.ImportFrom)) and any(
            alias.name not in WHITELISTED_LIBRARIES for alias in node.names
        )

    def is_df_overwrite(self, node: ast.stmt) -> str:
        """Remove df declarations from the code to prevent malicious code execution"""

        return (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "df"
        )

    def clean_code(self, code: str) -> str:
        """Clean the code to prevent malicious code execution"""

        tree = ast.parse(code)

        new_body = [
            node
            for node in tree.body
            if not (self.is_unsafe_import(node) or self.is_df_overwrite(node))
        ]

        new_tree = ast.Module(body=new_body)
        return astor.to_source(new_tree).strip()

    def run_code(
        self,
        code: str,
        data_frame: pd.DataFrame,
        use_error_correction_framework: bool = True,
    ) -> str:
        # pylint: disable=W0122 disable=W0123 disable=W0702:bare-except
        """Run the code in the current context and return the result"""

        # Get the code to run removing unsafe imports and df overwrites
        code_to_run = self.clean_code(code)
        self.last_run_code = code_to_run
        self.log(
            f"""
Code running:
```
{code_to_run}
```"""
        )

        # Redirect standard output to a StringIO buffer
        with redirect_stdout(io.StringIO()) as output:
            count = 0
            while count < self._max_retries:
                try:
                    # Execute the code
                    exec(
                        code_to_run,
                        {
                            "pd": pd,
                            "df": data_frame,
                            "plt": plt,
                            "__builtins__": {
                                **{
                                    builtin: __builtins__[builtin]
                                    for builtin in WHITELISTED_BUILTINS
                                },
                            },
                        },
                    )
                    code = code_to_run
                    break
                except Exception as e:  # pylint: disable=W0718 disable=C0103
                    if not use_error_correction_framework:
                        raise e

                    count += 1
                    error_correcting_instruction = CorrectErrorPrompt(
                        code=code,
                        error_returned=e,
                        question=self._original_instructions["question"],
                        df_head=self._original_instructions["df_head"],
                        num_rows=self._original_instructions["num_rows"],
                        num_columns=self._original_instructions["num_columns"],
                        rows_to_display=self._original_instructions["rows_to_display"],
                    )
                    code_to_run = self._llm.generate_code(
                        error_correcting_instruction, ""
                    )

        captured_output = output.getvalue()

        # Evaluate the last line and return its value or the captured output
        lines = code.strip().split("\n")
        last_line = lines[-1].strip()

        pattern = r"^print\((.*)\)$"
        match = re.match(pattern, last_line)
        if match:
            last_line = match.group(1)

        try:
            return eval(
                last_line,
                {
                    "pd": pd,
                    "df": data_frame,
                    "__builtins__": {
                        **{
                            builtin: __builtins__[builtin]
                            for builtin in WHITELISTED_BUILTINS
                        },
                    },
                },
            )
        except Exception:  # pylint: disable=W0718
            return captured_output

    def log(self, message: str):
        """Log a message"""
        if self._verbose:
            print(message)
