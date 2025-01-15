import pandas as pd


class DataframeSerializer:
    def __init__(self) -> None:
        pass

    def serialize(self, df: pd.DataFrame) -> str:
        """
        Convert df to csv like format where csv is wrapped inside <dataframe></dataframe>
        Args:
            df (pd.DataFrame): PandaAI dataframe or dataframe

        Returns:
            str: dataframe stringify
        """
        dataframe_info = "<table"

        # Add name attribute if available
        if df.name is not None:
            dataframe_info += f' table_name="{df.name}"'

        # Add description attribute if available
        if df.description is not None:
            dataframe_info += f' description="{df.description}"'

        dataframe_info += f' dimensions="{df.rows_count}x{df.columns_count}">'

        # Add dataframe details
        dataframe_info += f"\n{df.head().to_csv(index=False)}"

        # Close the dataframe tag
        dataframe_info += "</table>\n"

        return dataframe_info
