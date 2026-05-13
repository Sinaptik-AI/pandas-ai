import logging
import warnings
from typing import Any

from pandasai.config import Config
from pandasai.core.code_execution.environment import get_environment
from pandasai.exceptions import CodeExecutionError, NoResultFoundError


logger = logging.getLogger(__name__)


_SANDBOX_WARNING = (
    "pandas-ai is about to execute LLM-generated Python code on this host "
    "without a sandbox. This is the historical default but it is unsafe: "
    "if the LLM is influenced by untrusted input (a malicious prompt, a "
    "crafted CSV column, a poisoned tool response) the generated code can "
    "read files, exfiltrate environment variables, and run arbitrary "
    "subprocesses. Configure a Sandbox (e.g. pandasai_docker.DockerSandbox) "
    "via Agent(..., sandbox=...) to mitigate this. Pass "
    "Config(suppress_unsandboxed_warning=True) to silence this warning."
)


class CodeExecutor:
    """
    Handle the logic on how to handle different lines of code
    """

    _environment: dict

    def __init__(self, config: Config) -> None:
        self._environment = get_environment()
        self._config = config

    def add_to_env(self, key: str, value: Any) -> None:
        """
        Expose extra variables in the code to be used
        Args:
            key (str): Name of variable or lib alias
            value (Any): It can any value int, float, function, class etc.
        """
        self._environment[key] = value

    def _emit_sandbox_warning_once(self) -> None:
        """Warn (once per process) that code is about to run without a sandbox.

        ``exec(code, env)`` where ``env`` has no ``__builtins__`` key causes
        Python to silently insert the full ``builtins`` module, including
        ``__import__``, ``open``, ``eval``, ``exec``. LLM-generated code
        therefore has unrestricted access to the host. The DockerSandbox
        extension (or any subclass of :class:`pandasai.sandbox.Sandbox`)
        is the supported mitigation; this warning makes the unsandboxed
        default explicit so that users who haven't configured a sandbox
        notice and choose intentionally.
        """
        if getattr(self._config, "suppress_unsandboxed_warning", False):
            return
        if getattr(CodeExecutor, "_warned_unsandboxed", False):
            return
        CodeExecutor._warned_unsandboxed = True
        warnings.warn(_SANDBOX_WARNING, RuntimeWarning, stacklevel=3)
        logger.warning(_SANDBOX_WARNING)

    def execute(self, code: str) -> dict:
        self._emit_sandbox_warning_once()
        try:
            exec(code, self._environment)
        except Exception as e:
            raise CodeExecutionError("Code execution failed") from e
        return self._environment

    def execute_and_return_result(self, code: str) -> Any:
        """
        Executes the return updated environment
        """
        self.execute(code)

        # Get the result
        if "result" not in self._environment:
            raise NoResultFoundError(
                "No result was returned from the code execution. Please return the result in dictionary format, for example: result = {'type': ..., 'value': ...}"
            )

        return self._environment.get("result", None)

    @property
    def environment(self) -> dict:
        return self._environment
