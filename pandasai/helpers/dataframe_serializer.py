from enum import Enum
import json
import pandas as pd
import yaml


class DataframeSerializerType(Enum):
    JSON = 1
    YML = 2
    CSV = 3
    SQL = 4


class DataframeSerializer:
    def __init__(self) -> None:
        pass

    def serialize(
        self,
        df: pd.DataFrame,
        extras: dict = None,
        type_: DataframeSerializerType = DataframeSerializerType.YML,
    ) -> str:
        if type_ == DataframeSerializerType.YML:
            return self.convert_df_to_yml(df, extras)
        elif type_ == DataframeSerializerType.JSON:
            return self.convert_df_to_json_str(df, extras)
        elif type_ == DataframeSerializerType.SQL:
            return self.convert_df_sql_connector_to_str(df, extras)
        else:
            return self.convert_df_to_csv(df, extras)

    def convert_df_to_csv(self, df: pd.DataFrame, extras: dict) -> str:
        """
        Convert df to csv like format where csv is wrapped inside <dataframe></dataframe>
        Args:
            df (pd.DataFrame): PandasAI dataframe or dataframe
            extras (dict, optional): expect index to exists

        Returns:
            str: dataframe stringify
        """
        dataframe_info = "<dataframe"

        # Add name attribute if available
        if df.table_name is not None:
            dataframe_info += f' name="{df.table_name}"'

        # Add description attribute if available
        if df.table_description is not None:
            dataframe_info += f' description="{df.table_description}"'

        dataframe_info += ">"

        # Add dataframe details
        dataframe_info += f"\ndfs[{extras['index']}]:{df.rows_count}x{df.columns_count}\n{df.head_df.to_csv()}"

        # Close the dataframe tag
        dataframe_info += "</dataframe>"

        return dataframe_info

    def convert_df_sql_connector_to_str(
        self, df: pd.DataFrame, extras: dict = None
    ) -> str:
        """
        Convert df to csv like format where csv is wrapped inside <table></table>
        Args:
            df (pd.DataFrame): PandasAI dataframe or dataframe
            extras (dict, optional): expect index to exists

        Returns:
            str: dataframe stringify
        """
        table_description_tag = (
            f' description="{df.table_description}"'
            if df.table_description is not None
            else ""
        )
        table_head_tag = f'<table name="{df.table_name}"{table_description_tag}>'
        return f"{table_head_tag}\n{df.head_df.to_csv()}\n</table>"

    def convert_df_to_json(self, df: pd.DataFrame, extras: dict) -> dict:
        """
        Convert df to json dictionary and return json
        Args:
            df (pd.DataFrame): PandasAI dataframe or dataframe
            extras (dict, optional): expect index to exists

        Returns:
            str: dataframe json
        """
        # Initialize the result dictionary
        df_number_key = f"dfs[{extras['index']}]"
        result = {
            df_number_key: [
                {
                    "name": df.table_name,
                    "description": df.table_description,
                    "type": extras["type"],
                    "data": {},
                }
            ]
        }

        # Get DataFrame information
        num_rows, num_columns = df.shape

        # Add DataFrame details to the result
        result[df_number_key][0]["data"] = {
            "rows": num_rows,
            "columns": num_columns,
            "schema": {"fields": []},
        }

        # Iterate over DataFrame columns
        for col_name, col_dtype in df.dtypes.items():
            col_info = {
                "name": col_name,
                "type": str(col_dtype),
                "samples": df[col_name].sample(3).tolist()
                if num_rows > 5
                else df[col_name].head().tolist(),
            }

            # Add column description if available
            if df.field_descriptions and isinstance(df.field_descriptions, dict):
                if col_description := df.field_descriptions.get(col_name, None):
                    col_info["description"] = col_description

            result[df_number_key][0]["data"]["schema"]["fields"].append(col_info)

        return result

    def convert_df_to_json_str(self, df: pd.DataFrame, extras: dict) -> str:
        """
        Convert df to json and return it as string
        Args:
            df (pd.DataFrame): PandasAI dataframe or dataframe
            extras (dict, optional): expect index to exists

        Returns:
            str: dataframe stringify
        """
        return json.dumps(self.convert_df_to_json(df, extras))

    def convert_df_to_yml(self, df: pd.DataFrame, extras: dict) -> str:
        json_df = self.convert_df_to_json(df, extras)

        return yaml.dump(json_df, sort_keys=False)
