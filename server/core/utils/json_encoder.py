import datetime
import json
from json import JSONEncoder

import numpy as np
import pandas as pd


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)

        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)

        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        if isinstance(obj, (pd.Timestamp, datetime.datetime, datetime.date)):
            return obj.isoformat()

        return JSONEncoder.default(self, obj)


def jsonable_encoder(data: dict) -> dict:
    return json.loads(json.dumps(data, cls=CustomEncoder))
