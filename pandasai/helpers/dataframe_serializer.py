import typing

if typing.TYPE_CHECKING:
    from ..dataframe.base import DataFrame


class DataframeSerializer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def serialize(df: "DataFrame", dialect: str = "postgres") -> str:
        """
        Convert df to csv like format where csv is wrapped inside <dataframe></dataframe>
        Args:
            df (pd.DataFrame): PandaAI dataframe or dataframe

        Returns:
            str: dataframe stringify
        """
        dataframe_info = f'<table dialect="{dialect}" table_name="{df.schema.name}"'

        # Add description attribute if available
        if df.schema.description is not None:
            dataframe_info += f' description="{df.schema.description}"'

        dataframe_info += f' dimensions="{df.rows_count}x{df.columns_count}">'

        # Add dataframe details
        dataframe_info += f"\n{df.head().to_csv(index=False)}"

        # Close the dataframe tag
        dataframe_info += "</table>\n"

        return dataframe_info
