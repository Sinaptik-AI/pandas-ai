"""
This module contains helper functions for anonymizing data and generating random data
 before sending it to the LLM (An External API).

Only df.head() is sent to LLM API, hence the df.head() is processed
 to remove any personal or sensitive information.

"""

import random
import pandas as pd
import numpy as np

from .df_info import df_type, DataFrameType
from .anonymizer import Anonymizer


class DataSampler:
    def __init__(self, df: DataFrameType):
        """
        Args:
            df (SmartDataframe): SmartDataframe to sample from.
        """
        if df_type(df) == "polars":
            df = df.to_pandas()
        self.df = df

    def sample(self, n: int = 5) -> pd.DataFrame:
        """Sample the dataframe.

        Args:
            n (int, optional): Number of rows to sample. Defaults to 5.

        Returns:
            DataFrameType: Sampled dataframe.
        """
        sampled_df = pd.DataFrame()
        if len(self.df) <= n:
            sampled_df = self.df.sample(frac=1)
        else:
            for col in self.df.columns:
                col_sample = self._sample_column(col, n)
                sampled_df[col] = col_sample

        # anonymize the sampled dataframe head
        sampled_df = Anonymizer.anonymize_dataframe_head(sampled_df)

        return sampled_df

    def _sample_column(self, col: str, n: int) -> list:
        """Sample a column.

        Args:
            col (str): Column name.
            n (int): Number of rows to sample.

        Returns:
            list: Sampled column.
        """

        col_sample = []
        col_values = self.df[col].dropna().unique()

        # if there is a null value in the column, it MUST be included in the sample
        if self.df[col].isna().any():
            col_sample.append(np.nan)
            n -= 1

        # if the column has less than n unique values, then a random sample of the
        # unique values should be returned
        if len(col_values) <= n:
            col_sample.extend(col_values)
            n -= len(col_values)
        else:
            col_sample.extend(random.sample(list(col_values), n))
            n = 0

        # if there are still rows to sample, sample them randomly
        if n > 0 and len(col_values) > 0:
            col_sample.extend(random.choices(list(col_values), k=n))
        else:
            col_sample.extend([np.nan] * n)

        # shuffle the column sample before returning it
        random.shuffle(col_sample)
        return col_sample
