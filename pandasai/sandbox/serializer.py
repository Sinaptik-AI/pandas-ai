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
            return {"headers": [], "rows": []}

        json_data = df.to_dict(orient="split")
        return {"headers": json_data["columns"], "rows": json_data["data"]}

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
