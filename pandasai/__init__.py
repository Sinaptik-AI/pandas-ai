import pandas as pd
from .llm.base import LLM
import io
import sys

class PandasAI:
  """PandasAI is a wrapper around a LLM to make dataframes convesational"""

  instruction: str = """
There is a dataframe in pandas (python).
The name of the dataframe is `df`.
This is the result of `print(df.head())`:
{df}.

Return the python code (do not import anything) to get the answer to the following question:
"""
  llm: LLM

  # default constructor
  def __init__(self, llm = None):
    if llm is None:
      raise Exception("An LLM should be provided to instantiate a PandasAI instance")
    self.llm = llm

  def run(self, df: pd.DataFrame, prompt: str) -> str:
    """Run the LLM with the given prompt"""
    print(f"Running PandasAI with {self.llm._type} LLM...")
    result = self.llm.call(self.instruction.format(df = df.head()), prompt)
    return self.run_code(result, df)

  def run_code(self, code: str, df: pd.DataFrame):
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
    lines = code.strip().split('\n')
    last_line = lines[-1].strip()
    if last_line.startswith('print(') and last_line.endswith(')'):
      # last line is already printing
      return eval(last_line[6:-1])
    else:
      # evaluate last line and return its value or the captured output
      try:
        result = eval(last_line)
        return result
      except:
        return captured_output