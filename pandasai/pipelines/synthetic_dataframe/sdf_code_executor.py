from typing import Any
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.logic_units.code_executor import BaseCodeExecutor


class SDFCodeExecutor(BaseLogicUnit):
    """
    Executes the code generated by the prompt
    """

    _max_retries: int

    def __init__(self) -> None:
        self._max_retries = 0

    def execute(self, input: Any, **kwargs) -> Any:
        code_exec = BaseCodeExecutor()
        try:
            namespace = code_exec.execute(input, **kwargs)

            if "df" not in namespace:
                raise ValueError(f"Unable to execute code: {input}")

            return namespace["df"]
        except Exception:
            logger = kwargs.get("logger")
            if logger is not None:
                logger.log("Error in executing code")
            raise