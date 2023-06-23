from typing import Union
import pandas as pd
from abc import ABC, abstractmethod


class Shortcuts(ABC):
    @abstractmethod
    def run(self, df: pd.DataFrame, prompt: str) -> Union[str, pd.DataFrame]:
        """
        Run method from PandasAI class.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            prompt (str): The prompt to be executed.

        Returns:
            Union[str, pd.DataFrame]: The response from the LLM.
        """

        pass

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Do data cleaning and return the dataframe.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """

        return self.run(
            df,
            """
1. Copy the dataframe to a new variable named df_cleaned.
2. Do data cleaning.
3. Return df_cleaned.
""",
        )

    def impute_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Do missing value imputation and return the dataframe.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.

        Returns:
            pd.DataFrame: The DataFrame with imputed missing values.
        """

        return self.run(
            df,
            """
1. Copy the dataframe to a new variable named df_imputed.
2. Do the imputation of missing values.
3. Return df_imputed.
""",
        )

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Do feature generation and return the dataframe.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.

        Returns:
            pd.DataFrame: The DataFrame with generated features.
        """

        return self.run(
            df,
            """
1. Copy the dataframe to a new variable named df_features.
2. Do feature generation.
3. Return df_features.
""",
        )

    def plot_pie_chart(self, df: pd.DataFrame, labels: list, values: list) -> None:
        """
        Plot a pie chart.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            labels (list): The labels for the pie chart.
            values (list): The values for the pie chart.

        Returns:
            None
        """

        self.run(
            df,
            f"""
Plot a pie chart with the following labels and values:
labels = {labels}
values = {values}
""",
        )

    def plot_bar_chart(self, df: pd.DataFrame, x: list, y: list) -> None:
        """
        Plot a bar chart.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            x (list): The x values for the bar chart.
            y (list): The y values for the bar chart.

        Returns:
            None
        """

        self.run(
            df,
            f"""
Plot a bar chart with the following x and y:
x = {x}
y = {y}
""",
        )

    def plot_histogram(self, df: pd.DataFrame, column: str) -> None:
        """
        Plot a histogram.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column (str): The column to plot the histogram for.

        Returns:
            None
        """

        self.run(df, f"Plot a histogram of the column {column}.")

    def plot_line_chart(self, df: pd.DataFrame, x: list, y: list) -> None:
        """
        Plot a line chart.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            x (list): The x values for the line chart.
            y (list): The y values for the line chart.

        Returns:
            None
        """

        self.run(
            df,
            f"""
Plot a line chart with the following x and y:
x = {x}
y = {y}
""",
        )

    def plot_scatter_chart(self, df: pd.DataFrame, x: list, y: list) -> None:
        """
        Plot a scatter chart.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            x (list): The x values for the scatter chart.
            y (list): The y values for the scatter chart.

        Returns:
            None
        """

        self.run(
            df,
            f"""
Plot a scatter chart with the following x and y:
x = {x}
y = {y}
""",
        )

    def plot_correlation_heatmap(self, df: pd.DataFrame) -> None:
        """
        Plot a correlation heatmap.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.

        Returns:
            None
        """

        self.run(df, "Plot a correlation heatmap.")

    def plot_confusion_matrix(
        self, df: pd.DataFrame, y_true: list, y_pred: list
    ) -> None:
        """
        Plot a confusion matrix.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            y_true (list): The true values.
            y_pred (list): The predicted values.

        Returns:
            None
        """

        self.run(
            df,
            f"""
Plot a confusion matrix with the following y_true and y_pred:
y_true = {y_true}
y_pred = {y_pred}
""",
        )

    def plot_roc_curve(self, df: pd.DataFrame, y_true: list, y_pred: list) -> None:
        """
        Plot a ROC curve.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            y_true (list): The true values.
            y_pred (list): The predicted values.

        Returns:
            None
        """

        self.run(
            df,
            f"""
Plot a ROC curve with the following y_true and y_pred:
y_true = {y_true}
y_pred = {y_pred}
""",
        )

    def boxplot(
        self,
        df: pd.DataFrame,
        col: Union[str, list[str]] = None,
        by: Union[str, list[str]] = None,
        style: str = None,
    ):
        """
        Draw a box plot to show distributions with respect to categories.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            col (str | list[str] | None): The column(s) of interest
            for the box plot. Defaults to None.
            by (str | list[str] | None): The grouping variable(s)
            for the box plot. Defaults to None.
            style (str | None): The textual description of the desired
            style. Defaults to None.

        Returns:
            str: LLM response
        """

        if not isinstance(col, (str, list, type(None))):
            raise TypeError(
                "The 'col' argument must be a string, a list of strings, or None."
            )
        if not isinstance(by, (str, list, type(None))):
            raise TypeError(
                "The 'by' argument must be a string, a list of strings, or None."
            )

        prompt = "Plot a box-and-whisker plot"

        if isinstance(col, str):
            prompt += f" for the variable '{col}'"
        elif isinstance(col, list):
            var_list = [f"'{v}'" for v in col]
            if len(var_list) > 1:
                variables_str = ", ".join(var_list[:-1])
                prompt += f" for the variables {variables_str} and {var_list[-1]}"
            else:
                prompt += f" for the variable {var_list[0]}"

        if by is not None:
            prompt += f" grouped by '{by}'"

        if style is not None:
            prompt += f"\nStyle: '''{style}'''"

        self.run(df, prompt)

    def rolling_mean(self, df: pd.DataFrame, column: str, window: int) -> pd.DataFrame:
        """
        Calculate the rolling mean.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column (str): The column to calculate the rolling mean for.
            window (int): The window size.

        Returns:
            pd.DataFrame: The DataFrame containing the rolling mean.
        """

        return self.run(
            df,
            f"Calculate the rolling mean of the column {column} with a window"
            " of {window}.",
        )

    def rolling_median(
        self, df: pd.DataFrame, column: str, window: int
    ) -> pd.DataFrame:
        """
        Calculate the rolling median.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column (str): The column to calculate the rolling median for.
            window (int): The window size.

        Returns:
            pd.DataFrame: The DataFrame containing the rolling median.
        """

        return self.run(
            df,
            f"Calculate the rolling median of the column {column} with a window"
            " of {window}.",
        )

    def rolling_std(self, df: pd.DataFrame, column: str, window: int) -> pd.DataFrame:
        """
        Calculate the rolling standard deviation.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            column (str): The column to calculate the rolling standard deviation for.
            window (int): The window size.

        Returns:
            pd.DataFrame: The DataFrame containing the rolling standard deviation.
        """

        return self.run(
            df,
            f"Calculate the rolling standard deviation of the column {column} with a"
            "window of {window}.",
        )

    def segment_customers(
        self, df: pd.DataFrame, features: list, n_clusters: int
    ) -> pd.DataFrame:
        """
        Segment customers.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            features (list): The features to use for the segmentation.
            n_clusters (int): The number of clusters.

        Returns:
            pd.DataFrame: The DataFrame containing the segmentation.
        """

        return self.run(
            df,
            f"""
Segment customers with the following features and number of clusters:
features = {features}
n_clusters = {n_clusters}
""",
        )
