import os
import time
from typing import Any, List, TypedDict, Union

import requests


class ResponseType(TypedDict):
    type: str
    value: Any


exec_steps = {
    "cache_hit": "Cache Hit",
    "_get_prompt": "Generate Prompt",
    "generate_code": "Generate Code",
    "execute_code": "Code Execution",
    "_retry_run_code": "Retry Code Generation",
    "parse": "Parse Output",
}


class QueryExecTracker:
    _query_info: str = {}
    _dataframes: List = []
    _response: ResponseType = {}
    _steps: List = []
    _start_time = None
    _success: bool = False
    _server_config: dict = None

    def __init__(
        self,
        conversation_id: str,
        query: str,
        instance: str,
        output_type: str,
        server_config: Union[dict, None] = None,
    ) -> None:
        self._start_time = time.time()
        self._success = False
        self._server_config = server_config
        self._query_info = {
            "conversation_id": str(conversation_id),
            "query": query,
            "instance": instance,
            "output_type": output_type,
        }

    def add_dataframes(self, dfs: List) -> None:
        """
        Add used dataframes for the query to query exec tracker
        Args:
            dfs (List[SmartDataFrame]): List of dataframes
        """
        for df in dfs:
            head = df.head_df
            self._dataframes.append(
                {"headers": head.columns.tolist(), "rows": head.values.tolist()}
            )

    def add_step(self, step: dict) -> None:
        """
        Add Custom Step that is performed for additional information
        Args:
            step (dict): dictionary containing information
        """
        self._steps.append(step)

    def execute_func(self, function, *args, **kwargs) -> Any:
        """
        Tracks function executions, calculates execution time and prepare data
        Args:
            function (function): Function that is to be executed

        Returns:
            Any: Response return after function execution
        """
        start_time = time.time()

        # Get the tag from kwargs if provided, or use the function name as the default
        tag = kwargs.pop("tag", function.__name__)

        try:
            result = function(*args, **kwargs)

            execution_time = time.time() - start_time
            if tag not in exec_steps:
                return result

            step_data = self._generate_exec_step(tag, result)

            step_data["type"] = exec_steps[tag]
            step_data["success"] = True
            step_data["execution_time"] = execution_time

            self._steps.append(step_data)

            return result

        except Exception:
            execution_time = time.time() - start_time
            self._steps.append(
                {
                    "type": exec_steps[tag],
                    "success": False,
                    "execution_time": execution_time,
                }
            )
            raise

    def _generate_exec_step(self, func_name: str, result: Any) -> dict:
        """
        Extracts and Generates result
        Args:
            func_name (str): function name that is executed
            result (Any): function output response

        Returns:
            dict: dictionary with information about the function execution
        """
        if (
            func_name == "cache_hit"
            or func_name == "generate_code"
            or func_name == "_retry_run_code"
        ):
            return {"code_generated": result}
        elif func_name == "_get_prompt":
            return {
                "prompt_class": result.__class__.__name__,
                "generated_prompt": result.to_string(),
            }
        elif func_name == "execute_code":
            self._response = self._format_response(result)
            return {"result": self._response}
        else:
            return {}

    def _format_response(self, result: ResponseType) -> ResponseType:
        """
        Format output response
        Args:
            result (ResponseType): response returned after execution

        Returns:
            ResponseType: formatted response output
        """
        formatted_result = {}
        if result["type"] == "dataframe":
            formatted_result = {
                "type": result["type"],
                "value": {
                    "headers": result["value"].columns.tolist(),
                    "rows": result["value"].values.tolist(),
                },
            }
            return formatted_result
        else:
            return result

    def get_summary(self) -> dict:
        """
        Returns the summary in json to steps involved in execution of track
        Returns:
            dict: summary json
        """
        execution_time = time.time() - self._start_time
        return {
            "query_info": self._query_info,
            "dataframes": self._dataframes,
            "steps": self._steps,
            "response": self._response,
            "execution_time": execution_time,
            "success": self._success,
        }

    def get_execution_time(self) -> float:
        return time.time() - self._start_time

    def publish(self) -> None:
        """
        Publish Query Summary to remote logging server
        """
        api_key = None
        server_url = None

        if self._server_config is None:
            server_url = os.environ.get("LOGGING_SERVER_URL")
            api_key = os.environ.get("LOGGING_SERVER_API_KEY")
        else:
            server_url = self._server_config.get(
                "server_url", os.environ.get("LOGGING_SERVER_URL")
            )
            api_key = self._server_config.get(
                "api_key", os.environ.get("LOGGING_SERVER_API_KEY")
            )

        if api_key is None or server_url is None:
            return

        try:
            log_data = {
                "json_log": self.get_summary(),
            }
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.post(
                f"{server_url}/api/log/add", json=log_data, headers=headers
            )
            if response.status_code != 200:
                raise Exception(response.text)

        except Exception as e:
            print(f"Exception in APILogger: {e}")

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, value):
        self._success = value
