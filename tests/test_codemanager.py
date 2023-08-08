"""Unit tests for the CodeManager class"""
from typing import Optional
from unittest.mock import Mock

import pandas as pd
import pytest

from pandasai.exceptions import BadImportError, NoCodeFoundError
from pandasai.llm.fake import FakeLLM

from pandasai.smart_dataframe import SmartDataframe

from pandasai.helpers.code_manager import CodeManager


class TestCodeManager:
    """Unit tests for the CodeManager class"""

    @pytest.fixture
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

    @pytest.fixture
    def smart_dataframe(self, llm, sample_df):
        return SmartDataframe(sample_df, config={"llm": llm, "enable_cache": False})

    @pytest.fixture
    def code_manager(self, smart_dataframe: SmartDataframe):
        return smart_dataframe.lake._code_manager

    def test_run_code_for_calculations(self, code_manager: CodeManager):
        code = """def analyze_data(dfs):
    return {'type': 'number', 'value': 1 + 1}"""

        assert code_manager.execute_code(code, "")["value"] == 2
        assert code_manager.last_code_executed == code

    def test_run_code_invalid_code(self, code_manager: CodeManager):
        with pytest.raises(Exception):
            code_manager.execute_code("1+ ", "")

    def test_clean_code_remove_builtins(self, code_manager: CodeManager):
        builtins_code = """import set
def analyze_data(dfs):
    return {'type': 'number', 'value': set([1, 2, 3])}"""
        assert code_manager.execute_code(builtins_code, "")["value"] == {1, 2, 3}
        assert (
            code_manager.last_code_executed
            == """def analyze_data(dfs):
    return {'type': 'number', 'value': set([1, 2, 3])}"""
        )

    def test_clean_code_removes_jailbreak_code(self, code_manager: CodeManager):
        malicious_code = """def analyze_data(dfs):
    __builtins__['str'].__class__.__mro__[-1].__subclasses__()[140].__init__.__globals__['system']('ls')
    print('hello world')"""
        assert (
            code_manager._clean_code(malicious_code)
            == """def analyze_data(dfs):
    print('hello world')"""
        )

    def test_clean_code_remove_environment_defaults(self, code_manager: CodeManager):
        pandas_code = """import pandas as pd
print('hello world')
"""
        assert code_manager._clean_code(pandas_code) == "print('hello world')"

    def test_clean_code_whitelist_import(self, code_manager: CodeManager):
        """Test that an installed whitelisted library is added to the environment."""
        safe_code = """
import numpy as np
np.array()
"""
        assert code_manager._clean_code(safe_code) == "np.array()"

    def test_clean_code_raise_bad_import_error(self, code_manager: CodeManager):
        malicious_code = """
import os
print(os.listdir())
"""
        with pytest.raises(BadImportError):
            code_manager.execute_code(malicious_code, "")

    def test_remove_dfs_overwrites(self, code_manager: CodeManager):
        hallucinated_code = """def analyze_data(dfs):
    dfs = [pd.DataFrame([1,2,3])]
    print(dfs)"""
        assert (
            code_manager._clean_code(hallucinated_code)
            == """def analyze_data(dfs):
    print(dfs)"""
        )

    def test_exception_handling(
        self, smart_dataframe: SmartDataframe, code_manager: CodeManager
    ):
        code_manager.execute_code = Mock(
            side_effect=NoCodeFoundError("No code found in the answer.")
        )

        result = smart_dataframe.chat("How many countries are in the dataframe?")
        assert result == (
            "Unfortunately, I was not able to answer your question, "
            "because of the following error:\n"
            "\nNo code found in the answer.\n"
        )
        assert smart_dataframe.last_error == "No code found in the answer."

    def test_custom_whitelisted_dependencies(self, code_manager: CodeManager, llm):
        code = """
import my_custom_library
def analyze_data(self, dfs: list):
    my_custom_library.do_something()
"""
        llm._output = code

        with pytest.raises(BadImportError):
            code_manager._clean_code(code)

        code_manager._config.custom_whitelisted_dependencies = ["my_custom_library"]
        assert (
            code_manager._clean_code(code)
            == """def analyze_data(self, dfs: list):
    my_custom_library.do_something()"""
        )

    def test_get_environment(self, code_manager: CodeManager, smart_dataframe):
        code_manager._additional_dependencies = [
            {"name": "pyplot", "alias": "plt", "module": "matplotlib"},
            {"name": "numpy", "alias": "np", "module": "numpy"},
        ]

        assert "pd" in code_manager._get_environment()
        assert "plt" in code_manager._get_environment()
        assert "np" in code_manager._get_environment()
        assert code_manager._get_environment()["__builtins__"] == {
            "abs": abs,
            "all": all,
            "any": any,
            "ascii": ascii,
            "bin": bin,
            "bool": bool,
            "bytearray": bytearray,
            "bytes": bytes,
            "callable": callable,
            "chr": chr,
            "classmethod": classmethod,
            "complex": complex,
            "delattr": delattr,
            "dict": dict,
            "dir": dir,
            "divmod": divmod,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "format": format,
            "frozenset": frozenset,
            "getattr": getattr,
            "hasattr": hasattr,
            "hash": hash,
            "help": help,
            "hex": hex,
            "id": id,
            "input": input,
            "int": int,
            "isinstance": isinstance,
            "issubclass": issubclass,
            "iter": iter,
            "len": len,
            "list": list,
            "locals": locals,
            "map": map,
            "max": max,
            "memoryview": memoryview,
            "min": min,
            "next": next,
            "object": object,
            "oct": oct,
            "ord": ord,
            "pow": pow,
            "print": print,
            "property": property,
            "range": range,
            "repr": repr,
            "reversed": reversed,
            "round": round,
            "set": set,
            "setattr": setattr,
            "slice": slice,
            "sorted": sorted,
            "staticmethod": staticmethod,
            "str": str,
            "sum": sum,
            "super": super,
            "tuple": tuple,
            "type": type,
            "vars": vars,
            "zip": zip,
            "__build_class__": __build_class__,
            "__name__": "__main__",
        }
