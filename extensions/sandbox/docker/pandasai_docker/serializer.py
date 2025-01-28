import base64
import datetime
import json
import os  # important to import
import tarfile  # important to import
from json import JSONEncoder

import numpy as np
import pandas as pd


class ResponseSerializer:
    @staticmethod
    def serialize_dataframe(df: pd.DataFrame) -> dict:
        if df.empty:
            return {"columns": [], "data": [], "index": []}
        return df.to_dict(orient="split")

    @staticmethod
    def serialize(result: dict) -> str:
        if result["type"] == "dataframe":
            if isinstance(result["value"], pd.Series):
                result["value"] = result["value"].to_frame()
            result["value"] = ResponseSerializer.serialize_dataframe(result["value"])

        elif result["type"] == "plot" and isinstance(result["value"], str):
            with open(result["value"], "rb") as image_file:
                image_data = image_file.read()
            result["value"] = base64.b64encode(image_data).decode()

        return json.dumps(result, cls=CustomEncoder)

    @staticmethod
    def deserialize(response: str, chart_path: str = None) -> dict:
        result = json.loads(response)
        if result["type"] == "dataframe":
            json_data = result["value"]
            result["value"] = pd.DataFrame(
                data=json_data["data"],
                index=json_data["index"],
                columns=json_data["columns"],
            )

        elif result["type"] == "plot" and chart_path:
            image_data = base64.b64decode(result["value"])

            # Write the binary data to a file
            with open(chart_path, "wb") as image_file:
                image_file.write(image_data)

            result["value"] = chart_path

        return result


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)

        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)

        if isinstance(obj, (pd.Timestamp, datetime.datetime, datetime.date)):
            return obj.isoformat()

        if isinstance(obj, pd.DataFrame):
            return ResponseSerializer.serialize_dataframe(obj)

        return super().default(obj)


parser = ResponseSerializer()
