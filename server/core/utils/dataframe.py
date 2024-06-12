import json

import pandas as pd


def convert_dataframe_to_dict(df: pd.DataFrame):
    json_data = json.loads(
        df.to_json(
            orient="split",
            date_format="iso",
            default_handler=str,
            force_ascii=False,
        )
    )
    return {"headers": json_data["columns"], "rows": json_data["data"]}


def load_df(data: dict):
    return pd.DataFrame(data["rows"], columns=data["headers"])
