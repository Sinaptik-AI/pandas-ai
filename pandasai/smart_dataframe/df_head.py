import pandas as pd
from ..helpers.data_sampler import DataSampler
from ..helpers.df_info import DataFrameType, df_type
from ..connectors.base import BaseConnector
from functools import cache


class DataframeHead:
    is_connector = None

    def __init__(
        self,
        df: DataFrameType,
        custom_head: pd.DataFrame = None,
        samples_amount: int = 3,
    ):
        if custom_head is not None:
            self.custom_head = custom_head
        elif isinstance(df, BaseConnector):
            self.custom_head = None
            self.is_connector = True
            self.connector = df
        else:
            sampler = DataSampler(df)
            self.custom_head = sampler.sample(samples_amount)

    def head_with_truncate_columns(self, max_size=25) -> DataFrameType:
        """
        Truncate the columns of the dataframe to a maximum of 20 characters.

        Args:
            df (DataFrameType): Pandas or Polars dataframe

        Returns:
            DataFrameType: Pandas or Polars dataframe
        """

        if df_type(self.custom_head) == "pandas":
            df_trunc = self.custom_head.copy()

            for col in self.custom_head.columns:
                if self.custom_head[col].dtype == "object":
                    first_val = self.custom_head[col].iloc[0]
                    if isinstance(first_val, str) and len(first_val) > max_size:
                        df_trunc[col] = df_trunc[col].str.slice(0, max_size - 3) + "..."
        elif df_type(self.custom_head) == "polars":
            try:
                import polars as pl

                df_trunc = self.custom_head.clone()

                for col in self.custom_head.columns:
                    if self.custom_head[col].dtype == pl.Utf8:
                        first_val = self.custom_head[col][0]
                        if isinstance(first_val, str) and len(df_trunc[col]) > max_size:
                            df_trunc[col] = (
                                df_trunc[col].str.slice(0, max_size - 3) + "..."
                            )
            except ImportError as e:
                raise ImportError(
                    "Polars is not installed. "
                    "Please install Polars to use this feature."
                ) from e

        return df_trunc

    def load_if_connector(self):
        """
        Load the connector if it is a connector in order to lazy load the data.
        """
        if self.is_connector:
            self.custom_head = self.connector.head()

    @cache
    def sample(self) -> pd.DataFrame:
        """
        A sample of the dataframe.

        Returns:
            pd.DataFrame: A sample of the dataframe.
        """
        self.load_if_connector()

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
        self.load_if_connector()

        return self.custom_head.to_csv(index=False)
