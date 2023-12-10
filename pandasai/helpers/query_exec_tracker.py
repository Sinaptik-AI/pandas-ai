import base64
import json
import os
import time
from typing import Any, List, TypedDict, Union
import uuid

import requests
from collections import defaultdict


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
    _query_info: dict
    _dataframes: List
    _response: ResponseType
    _steps: List
    _func_exec_count: dict
    _success: bool
    _server_config: dict
    _last_log_id: int

    def __init__(
        self,
        server_config: Union[dict, None] = None,
    ) -> None:
        self._success = False
        self._start_time = None
        self._server_config = server_config
        self._query_info = {}
        self._is_related_query = True

    def set_related_query(self, flag: bool):
        """
        Set Related Query Parameter whether new query is related to the conversation
        or not
        Args:
            flag (bool): boolean to set true if related else false
        """
        self._is_related_query = flag

    def add_query_info(
        self,
        conversation_id: uuid.UUID,
        instance: str,
        query: str,
        output_type: str,
    ):
        """
        Adds query information for new track
        Args:
            conversation_id (str): conversation id
            instance (str): instance like Agent or SmartDataframe
            query (str): chat query given by user
            output_type (str): output type expected by user
        """
        self._query_info = {
            "conversation_id": str(conversation_id),
            "instance": instance,
            "query": query,
            "output_type": output_type,
            "is_related_query": self._is_related_query,
        }

    def start_new_track(self):
        """
        Resets tracking variables to start new track
        """
        self._last_log_id = None
        self._start_time = time.time()
        self._dataframes: List = []
        self._response: ResponseType = {}
        self._steps: List = []
        self._query_info = {}
        self._func_exec_count: dict = defaultdict(int)

    def convert_dataframe_to_dict(self, df):
        json_data = json.loads(df.to_json(orient="split", date_format="iso"))
        return {"headers": json_data["columns"], "rows": json_data["data"]}

    def add_dataframes(self, dfs: List) -> None:
        """
        Add used dataframes for the query to query exec tracker
        Args:
            dfs (List[SmartDataFrame]): List of dataframes
        """
        for df in dfs:
            head = df.head_df
            self._dataframes.append(self.convert_dataframe_to_dict(head))

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

        step = {"type": exec_steps[func_name]}

        if func_name == "_get_prompt":
            step["prompt_class"] = result.__class__.__name__
            step["generated_prompt"] = result.to_string()

        elif func_name == "_retry_run_code":
            self._func_exec_count["_retry_run_code"] += 1

            step[
                "type"
            ] = f"{exec_steps[func_name]} ({self._func_exec_count['_retry_run_code']})"
            step["code_generated"] = result

        elif func_name in {"cache_hit", "generate_code"}:
            step["code_generated"] = result

        elif func_name == "execute_code":
            self._response = self._format_response(result)
            step["result"] = self._response

        return step

    def _format_response(self, result: ResponseType) -> ResponseType:
        """
        Format output response
        Args:
            result (ResponseType): response returned after execution

        Returns:
            ResponseType: formatted response output
        """
        if result["type"] == "dataframe":
            df_dict = self.convert_dataframe_to_dict(result["value"])
            return {"type": result["type"], "value": df_dict}

        elif result["type"] == "plot":
            with open(result["value"], "rb") as image_file:
                image_data = image_file.read()
            # Encode the image data to Base64
            base64_image = (
                f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
            )
            return {
                "type": result["type"],
                "value": base64_image,
            }
        else:
            return result

    def get_summary(self) -> dict:
        """
        Returns the summary in json to steps involved in execution of track
        Returns:
            dict: summary json
        """
        if self._start_time is None:
            raise RuntimeError("[QueryExecTracker]: Tracking not started")

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

            json_data = json.loads(response.text)

            if "data" in json_data and json_data["data"] is not None:
                self._last_log_id = json_data["data"]["log_id"]

        except Exception as e:
            print(f"Exception in APILogger: {e}")

    @property
    def success(self) -> bool:
        return self._success

    @success.setter
    def success(self, value: bool):
        self._success = value

    @property
    def last_log_id(self) -> int:
        return self._last_log_id
