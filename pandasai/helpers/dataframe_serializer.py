import json
from enum import Enum

import pandasai.pandas as pd


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
        if df.name is not None:
            dataframe_info += f' name="{df.name}"'

        # Add description attribute if available
        if df.description is not None:
            dataframe_info += f' description="{df.description}"'

        dataframe_info += ">"

        # Add dataframe details
        dataframe_info += f"\ndfs[{extras['index']}]:{df.rows_count}x{df.columns_count}\n{df.to_csv()}"

        # Close the dataframe tag
        dataframe_info += "</dataframe>\n"

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
            f' description="{df.description}"' if df.description is not None else ""
        )
        table_head_tag = f'<table name="{df.name}"{table_description_tag}>'
        return f"{table_head_tag}\n{df.get_head().to_csv()}\n</table>"

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

        # Create a dictionary representing the data structure
        df_info = {
            "name": df.name,
            "description": df.description,
            "type": (
                df.type
                if "is_direct_sql" in extras and extras["is_direct_sql"]
                else extras["type"]
            ),
        }
        # Add DataFrame details to the result
        data = {
            "rows": df.rows_count,
            "columns": df.columns_count,
            "schema": {"fields": []},
        }

        # Iterate over DataFrame columns
        df_head = df.get_head()
        for col_name, col_dtype in df_head.dtypes.items():
            col_info = {
                "name": col_name,
                "type": str(col_dtype),
            }

            if not extras.get("enforce_privacy") or df.custom_head is not None:
                col_info["samples"] = df_head[col_name].head().tolist()

            # Add column description if available
            if df.field_descriptions and isinstance(df.field_descriptions, dict):
                if col_description := df.field_descriptions.get(col_name, None):
                    col_info["description"] = col_description

            if df.connector_relations:
                for relation in df.connector_relations:
                    from pandasai.ee.connectors.relations import ForeignKey, PrimaryKey

                    if (
                        isinstance(relation, PrimaryKey) and relation.name == col_name
                    ) or (
                        isinstance(relation, ForeignKey) and relation.field == col_name
                    ):
                        col_info["constraints"] = relation.to_string()

            data["schema"]["fields"].append(col_info)

        result = df_info | data

        if "is_direct_sql" in extras and extras["is_direct_sql"]:
            return result

        return {df_number_key: result}

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

        import yaml

        yml_str = yaml.dump(json_df, sort_keys=False, allow_unicode=True)
        if "is_direct_sql" in extras and extras["is_direct_sql"]:
            return f"<table>\n{yml_str}\n</table>\n"
        return yml_str
