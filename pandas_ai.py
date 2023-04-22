import pandas as pd
from llm.base import LLM

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
    self.run_code(result, df)

  def run_code(self, code: str, df: pd.DataFrame):
    """Run the code in the current context and print the result"""

    # Execute the code
    exec(code)

    # Evaluate the last line and print its value (if not already printed)
    lines = code.strip().split('\n')
    last_line = lines[-1].strip()
    if last_line.startswith('print(') and last_line.endswith(')'):
      # last line is already printing
      pass
    else:
      # evaluate last line and print its value
      print(eval(last_line))