# -*- coding: utf-8 -*-
""" PandasAI is a wrapper around a LLM to make dataframes conversational

This module includes the implementation of basis  PandasAI class with methods to run the LLMs
models on Pandas dataframes. Following LLMs are implemented so far.

Example:

    This module is the Entry point of the `pandasai` package. Following is an example of how to
    use this Class.

    ```python
    import pandas as pd
    from pandasai import PandasAI

    # Sample DataFrame
    df = pd.DataFrame({
        "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain",
        "Canada", "Australia", "Japan", "China"],
        "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416,
        1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
        "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
    })

    # Instantiate a LLM
    from pandasai.llm.openai import OpenAI
    llm = OpenAI(api_token="YOUR_API_TOKEN")

    pandas_ai = PandasAI(llm, conversational=False)
    pandas_ai(df, prompt='Which are the 5 happiest countries?')

    ```
"""
import ast
import io
import re
from contextlib import redirect_stdout
from typing import Optional

import astor
import matplotlib.pyplot as plt
import pandas as pd

from .constants import (
    WHITELISTED_BUILTINS,
    WHITELISTED_LIBRARIES,
    WHITELISTED_OPTIONAL_LIBRARIES,
)
from .exceptions import BadImportError, LLMNotFoundError
from .helpers._optional import import_optional_dependency
from .helpers.anonymizer import anonymize_dataframe_head
from .helpers.notebook import Notebook
from .helpers.save_chart import add_save_chart
from .llm.base import LLM
from .prompts.correct_error_prompt import CorrectErrorPrompt
from .prompts.correct_multiples_prompt import CorrectMultipleDataframesErrorPrompt
from .prompts.generate_python_code import GeneratePythonCodePrompt
from .prompts.generate_response import GenerateResponsePrompt
from .prompts.multiple_dataframes import MultipleDataframesPrompt


# pylint: disable=too-many-instance-attributes disable=too-many-arguments
class PandasAI:
    """PandasAI is a wrapper around a LLM to make dataframes conversational.


    This is a an entry point of `pandasai` object. This class consists of methods to interface the
    LLMs with Pandas     dataframes. A pandas dataframe metadata i.e df.head() and prompt is
    passed on to chosen LLMs API end point to     generate a Python code to answer the questions
    asked. The resultant python code is run on actual data and answer is converted into a
    conversational form.

    Note:
        Do not include the `self` parameter in the ``Args`` section.
    Args:
        _llm (obj): LLMs option to be used for API access
        _verbose (bool, optional): To show the intermediate outputs e.g python code
        generated and execution step on the prompt. Default to False
        _is_conversational_answer (bool, optional): Whether to return answer in conversational
        form. Default to False
        _enforce_privacy (bool, optional): Do not display the data on prompt in case of
        Sensitive data. Default to False
        _max_retries (int, optional): max no. of tries to generate code on failure. Default to 3
        _is_notebook (bool, optional): Whether to run code in notebook. Default to False
        _original_instructions (dict, optional): The dict of instruction to run. Default to None
        last_code_generated (str, optional): Pass last Code if generated. Default to None
        last_run_code (str, optional): Pass the last execution / run. Default to None
        code_output (str, optional): The code output if any. Default to None
        last_error (str, optional): Error of running code last time. Default to None


    Returns:
        response (str): Returns the Response to a Question related to Data

    """

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
        save_charts=False,
    ):
        """

        __init__ method of the Class PandasAI

        Args:
            llm (object): LLMs option to be used for API access. Default is None
            conversational (bool): Whether to return answer in conversational form. Default to True
            verbose (bool): To show the intermediate outputs e.g python code generated and
             execution step on the prompt.  Default to False
            enforce_privacy (bool): Execute the codes with Privacy Mode ON.  Default to False
        """
        if llm is None:
            raise LLMNotFoundError(
                "An LLM should be provided to instantiate a PandasAI instance"
            )
        self._llm = llm
        self._is_conversational_answer = conversational
        self._verbose = verbose
        self._enforce_privacy = enforce_privacy
        self._save_charts = save_charts

        self.notebook = Notebook()
        self._in_notebook = self.notebook.in_notebook()

    def conversational_answer(self, question: str, answer: str) -> str:
        """Returns the answer in conversational form about the resultant data.

        Args:
            question (str): A question in Conversational form
            answer (str): A summary / resultant Data

        Returns (str): Response

        """

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
        """
        Run the PandasAI to make Dataframes Conversational.

        Args:
            data_frame (pd.Dataframe): A pandas Dataframe
            prompt (str): A prompt to query about the Dataframe
            is_conversational_answer (bool): Whether to return answer in conversational form.
            Default to False
            show_code (bool): To show the intermediate python code generated on the prompt.
            Default to False
            anonymize_df (bool): Running the code with Sensitive Data. Default to True
            use_error_correction_framework (bool): Turn on Error Correction mechanism.
            Default to True

        Returns: Answer to the Input Questions about the DataFrame

        """

        self.log(f"Running PandasAI with {self._llm.type} LLM...")

        try:
            rows_to_display = 0 if self._enforce_privacy else 5

            multiple: bool = isinstance(data_frame, list)

            if multiple:
                heads = [
                    anonymize_dataframe_head(dataframe)
                    if anonymize_df
                    else dataframe.head(rows_to_display)
                    for dataframe in data_frame
                ]

                code = self._llm.generate_code(
                    MultipleDataframesPrompt(dataframes=heads),
                    prompt,
                )

                self._original_instructions = {
                    "question": prompt,
                    "df_head": heads,
                    "rows_to_display": rows_to_display,
                }

            else:
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
                    ```
                """
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
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{exception}\n"
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
        """
        __call__ method of PandasAI class. It call `run` method
        Args:
            data_frame:
            prompt:
            is_conversational_answer:
            show_code:
            anonymize_df:
            use_error_correction_framework:

        Returns:

        """

        return self.run(
            data_frame,
            prompt,
            is_conversational_answer,
            show_code,
            anonymize_df,
            use_error_correction_framework,
        )

    def _is_unsafe_import(self, node: ast.stmt) -> bool:
        """Remove non-whitelisted imports from the code to prevent malicious code execution

        Args:
            node (object): ast.stmt

        Returns (bool): A flag if unsafe_imports found.

        """

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name in WHITELISTED_BUILTINS:
                    return True
                if alias.name in WHITELISTED_OPTIONAL_LIBRARIES:
                    import_optional_dependency(alias.name)
                    continue
                if alias.name not in WHITELISTED_LIBRARIES:
                    raise BadImportError(alias.name)

        return False

    def _is_df_overwrite(self, node: ast.stmt) -> str:
        """
        Remove df declarations from the code to prevent malicious code execution. A helper method.
        Args:
            node (object): ast.stmt

        Returns (str):

        """

        return (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and re.match(r"df\d{0,2}$", node.targets[0].id)
        )

    def _clean_code(self, code: str) -> str:
        """
        A method to clean the code to prevent malicious code execution
        Args:
            code(str): A python code

        Returns (str): Returns a Clean Code String

        """

        tree = ast.parse(code)

        new_body = [
            node
            for node in tree.body
            if not (self._is_unsafe_import(node) or self._is_df_overwrite(node))
        ]

        new_tree = ast.Module(body=new_body)
        return astor.to_source(new_tree).strip()

    def run_code(
        self,
        code: str,
        data_frame: pd.DataFrame,
        use_error_correction_framework: bool = True,
    ) -> str:
        """
        A method to execute the python code generated by LLMs to answer the question about the
        input dataframe. Run the code in the current context and return the result.
        Args:
            code (str): A python code to execute
            data_frame (pd.DataFrame): A full Pandas DataFrame
            use_error_correction_framework (bool): Turn on Error Correction mechanism.
            Default to True

        Returns:

        """

        # pylint: disable=W0122 disable=W0123 disable=W0702:bare-except

        multiple: bool = isinstance(data_frame, list)

        # Add save chart code
        if self._save_charts:
            code = add_save_chart(code)

        # Get the code to run removing unsafe imports and df overwrites
        code_to_run = self._clean_code(code)
        self.last_run_code = code_to_run
        self.log(
            f"""
Code running:
```
{code_to_run}
```"""
        )

        environment: dict = {
            "pd": pd,
            "plt": plt,
            "__builtins__": {
                **{builtin: __builtins__[builtin] for builtin in WHITELISTED_BUILTINS},
            },
        }

        if multiple:
            environment.update(
                {f"df{i}": dataframe for i, dataframe in enumerate(data_frame, start=1)}
            )

        else:
            environment["df"] = data_frame

        # Redirect standard output to a StringIO buffer
        with redirect_stdout(io.StringIO()) as output:
            count = 0
            while count < self._max_retries:
                try:
                    # Execute the code
                    exec(code_to_run, environment)
                    code = code_to_run
                    break
                except Exception as e:  # pylint: disable=W0718 disable=C0103
                    if not use_error_correction_framework:
                        raise e

                    count += 1

                    if multiple:
                        error_correcting_instruction = (
                            CorrectMultipleDataframesErrorPrompt(
                                code=code,
                                error_returned=e,
                                question=self._original_instructions["question"],
                                df_head=self._original_instructions["df_head"],
                            )
                        )

                    else:
                        error_correcting_instruction = CorrectErrorPrompt(
                            code=code,
                            error_returned=e,
                            question=self._original_instructions["question"],
                            df_head=self._original_instructions["df_head"],
                            num_rows=self._original_instructions["num_rows"],
                            num_columns=self._original_instructions["num_columns"],
                            rows_to_display=self._original_instructions[
                                "rows_to_display"
                            ],
                        )

                    code_to_run = self._llm.generate_code(
                        error_correcting_instruction, ""
                    )

        captured_output = output.getvalue()

        # Evaluate the last line and return its value or the captured output
        lines = code.strip().split("\n")
        last_line = lines[-1].strip()

        match = re.match(r"^print\((.*)\)$", last_line)
        if match:
            last_line = match.group(1)

        try:
            return eval(last_line, environment)
        except Exception:  # pylint: disable=W0718
            return captured_output

    def log(self, message: str):
        """Log a message"""
        if self._verbose:
            print(message)
