import re
import ast

class LLM:
  @property
  def _type(self) -> str:
    """Return type of llm."""
    raise Exception("Type has not been implemented")
  
  def _remove_imports(self, code: str) -> str:
    tree = ast.parse(code)

    for node in tree.body[:]:
      if isinstance(node, ast.Import):
        for name in node.names:
          node.names.remove(name)
        if not node.names:
          tree.body.remove(node)
      elif isinstance(node, ast.ImportFrom):
        tree.body.remove(node)

    return ast.unparse(tree)

  def _polish_code(self, code: str) -> str:
    """Polish the code:
    - remove the leading "python" or "py"
    - remove the imports
    - remove trailing spaces and new lines
    """

    if re.match(r"^(python|py)", code):
      code = re.sub(r"^(python|py)", "", code)
    if re.match(r"^`.*`$", code):
      code = re.sub(r"^`(.*)`$", r"\1", code)
    self._remove_imports(code)
    code = code.strip()
    return code
  
  def _is_python_code(self, string):
    try:
      ast.parse(string)
      return True
    except SyntaxError:
      return False

  def _extract_code(self, response: str, separator: str = "```") -> str:
    """Extract the code from the response"""

    code = response
    if len(response.split(separator)) > 1:
      code = response.split(separator)[1]
    code = self._polish_code(code)
    if not self._is_python_code(code):
      raise Exception("No code found in the response")

    return code

  def call(self, instruction: str, input: str) -> str:
    """Execute the llm with the given prompt"""

    raise Exception("Call method has not been implemented")
  
  def generate_code(self, instruction: str, prompt: str) -> str:
    """Generate the code based on the instruction and the prompt"""

    return self._extract_code(self.call(instruction, prompt))