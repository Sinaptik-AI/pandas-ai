"""Unit tests for the base LLM class"""

import pytest

from pandasai.exceptions import APIKeyNotFoundError, NoCodeFoundError
from pandasai.helpers.memory import Memory
from pandasai.llm import LLM


class TestBaseLLM:
    """Unit tests for the base LLM class"""

    def test_type(self):
        with pytest.raises(APIKeyNotFoundError):
            LLM().type

    def test_is_pandasai_llm(self):
        assert LLM().is_pandasai_llm() is True

    def test_polish_code(self):
        code = "python print('Hello World')"
        assert LLM()._polish_code(code) == "print('Hello World')"
        code = "py print('Hello World')"
        assert LLM()._polish_code(code) == "print('Hello World')"
        code = "`print('Hello World')`"
        assert LLM()._polish_code(code) == "print('Hello World')"
        code = "``print('Hello World')``"
        assert LLM()._polish_code(code) == "`print('Hello World')`"
        code = "print('Hello World')"
        assert LLM()._polish_code(code) == "print('Hello World')"
        code = "import pandas as pd\nprint('Hello World')"
        assert LLM()._polish_code(code) == "import pandas as pd\nprint('Hello World')"

    def test_is_python_code(self):
        code = "python print('Hello World')"
        assert LLM()._is_python_code(code) is False
        code = "py print('Hello World')"
        assert LLM()._is_python_code(code) is False
        code = "`print('Hello World')`"
        assert LLM()._is_python_code(code) is False
        code = "print('Hello World')"
        assert LLM()._is_python_code(code) is True
        code = "1 +"
        assert LLM()._is_python_code(code) is False
        code = "1 + 1"
        assert LLM()._is_python_code(code) is True

    def test_extract_code(self):
        code = """Sure, here is your code:
```python
print('Hello World')
```
"""
        assert LLM()._extract_code(code) == "print('Hello World')"

        code = """Sure, here is your code:

```
print('Hello World')
```
"""
        assert LLM()._extract_code(code) == "print('Hello World')"

        code = """num_rows = dfs[0].shape[0]"""
        assert LLM()._extract_code(code) == "num_rows = dfs[0].shape[0]"

        code = """Sure, here is your code:

```py
print('Hello World')
```
"""
        assert LLM()._extract_code(code) == "print('Hello World')"

        code = """Sure, here is your code:

``py
print('Hello World')
``
"""
        with pytest.raises(NoCodeFoundError) as exc:
            LLM()._extract_code(code)
        assert "No code found" in str(exc.value)

        code = """Sure, here is your code:
`py
print('Hello World')
`
"""
        with pytest.raises(NoCodeFoundError) as exc:
            LLM()._extract_code(code)
        assert "No code found" in str(exc.value)

        code = """Sure, here is your code:
print('Hello World')
"""
        with pytest.raises(NoCodeFoundError) as exc:
            LLM()._extract_code(code)
        assert "No code found" in str(exc.value)

        code = """'''"""
        with pytest.raises(NoCodeFoundError) as exc:
            LLM()._extract_code(code)
        assert "No code found" in str(exc.value)

    def test_get_system_prompt_empty_memory(self):
        assert LLM().get_system_prompt(Memory()) == "\n"

    def test_get_system_prompt_memory_with_agent_info(self):
        mem = Memory(agent_info="xyz")
        assert LLM().get_system_prompt(mem) == " xyz \n"

    def test_get_system_prompt_memory_with_agent_info_messages(self):
        mem = Memory(agent_info="xyz", memory_size=10)
        mem.add("hello world", True)
        mem.add('print("hello world)', False)
        mem.add("hello world", True)
        print(mem.get_messages())
        assert (
            LLM().get_system_prompt(mem)
            == ' xyz \n\n### PREVIOUS CONVERSATION\n### QUERY\n hello world\n### ANSWER\n print("hello world)\n'
        )

    def test_prepend_system_prompt_with_empty_mem(self):
        assert LLM().prepend_system_prompt("hello world", Memory()) == "\nhello world"

    def test_prepend_system_prompt_with_non_empty_mem(self):
        mem = Memory(agent_info="xyz", memory_size=10)
        mem.add("hello world", True)
        mem.add('print("hello world)', False)
        mem.add("hello world", True)
        assert (
            LLM().prepend_system_prompt("hello world", mem)
            == ' xyz \n\n### PREVIOUS CONVERSATION\n### QUERY\n hello world\n### ANSWER\n print("hello world)\nhello world'
        )

    def test_prepend_system_prompt_with_memory_none(self):
        assert LLM().prepend_system_prompt("hello world", None) == "hello world"
