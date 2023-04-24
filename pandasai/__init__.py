import pandas as pd
from .llm.base import LLM
import io
import sys

class PandasAI:
  """PandasAI is a wrapper around a LLM to make dataframes convesational"""

  task_instruction: str = """
There is a dataframe in pandas (python).
The name of the dataframe is `df`.
This is the result of `print(df.columns)`:
{columns}.

Return the python code (do not import anything) to get the answer to the following question:
"""
  response_instruction: str = """
The customer asked:
{question}

To get the answer, run you run the following code in pandas (python):
{code}

Result:
{answer}

Write the answer to the customer
"""
  llm: LLM
  verbose: bool = False
  conversational_answer: bool = True

  def log(self, message: str):
    """Log a message"""
    if self.verbose:
      print(message)

  # default constructor
  def __init__(self, llm = None, conversational_answer = True, verbose = False):
    if llm is None:
      raise Exception("An LLM should be provided to instantiate a PandasAI instance")
    self.llm = llm
    self.conversational_answer = conversational_answer
    self.verbose = verbose

  def run(self, df: pd.DataFrame, prompt: str, conversational_answer: bool = None) -> str:
    """Run the LLM with the given prompt"""
    self.log(f"Running PandasAI with {self.llm._type} LLM...")
    code = self.llm.generate_code(self.task_instruction.format(columns = df.columns), prompt)
    self.log(f"""
Code generated:
```
{code}
```""")
    answer = self.run_code(code, df)
    self.log(f"Answer: {answer}")

    if conversational_answer is None:
      conversational_answer = self.conversational_answer
    if conversational_answer:
      answer = self.llm.call(self.response_instruction.format(question = prompt, code = code, answer = answer), answer)
      self.log(f"Conversational answer: {answer}")
    return answer

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