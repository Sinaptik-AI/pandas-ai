import pandas as pd
from ..connectors.base import BaseConnector
from functools import cache


class DataframeHead:
    def __init__(
        self,
        df: BaseConnector,
        custom_head: pd.DataFrame = None,
        samples_amount: int = 3,
    ):
        if custom_head is not None:
            self.custom_head = custom_head
        elif isinstance(df, BaseConnector):
            self.custom_head = df.head(samples_amount)
        else:
            raise ValueError("The dataframe must be a valid connector.")

    def head_with_truncate_columns(self, max_size=25) -> pd.DataFrame:
        """
        Truncate the columns of the dataframe to a maximum of 20 characters.

        Args:
            df (pd.DataFrame): The dataframe to truncate the columns of.

        Returns:
            pd.DataFrame: The dataframe with truncated columns.
        """
        df_trunc = self.custom_head.copy()

        for col in self.custom_head.columns:
            if self.custom_head[col].dtype == "object":
                first_val = self.custom_head[col].iloc[0]
                if isinstance(first_val, str) and len(first_val) > max_size:
                    df_trunc[col] = df_trunc[col].str.slice(0, max_size - 3) + "..."

        return df_trunc

    @cache
    def sample(self) -> pd.DataFrame:
        """
        A sample of the dataframe.

        Returns:
            pd.DataFrame: A sample of the dataframe.
        """
        if self.custom_head is None:
            return None

        if len(self.custom_head) > 0:
            return self.head_with_truncate_columns()

        return self.custom_head

    @cache
    def to_csv(self) -> str:
        """
        A proxy-call to the dataframe's `.to_csv()`.

        Returns:
            str: The dataframe as a CSV string.
        """
        return self.custom_head.to_csv(index=False)
