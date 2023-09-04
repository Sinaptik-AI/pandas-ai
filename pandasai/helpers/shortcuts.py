from ..helpers.df_info import DataFrameType
from typing import Union
from abc import ABC, abstractmethod


class Shortcuts(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> DataFrameType:
        """
        Run method from PandasAI class.

        Args:
            prompt (str): A prompt to be sent to LLM.

        Returns:
            DataFrameType: The response from the LLM.
        """

        pass

    def clean_data(self) -> DataFrameType:
        """
        Do data cleaning and return the dataframe.

        Returns:
            DataFrameType: The cleaned DataFrame.
        """

        return self.chat(
            """
1. Copy the dataframe to a new variable named df_cleaned.
2. Do data cleaning.
3. Return df_cleaned.
"""
        )

    def impute_missing_values(self) -> DataFrameType:
        """
        Do missing value imputation and return the dataframe.

        Returns:
            DataFrameType: The DataFrame with imputed missing values.
        """

        return self.chat(
            """
1. Copy the dataframe to a new variable named df_imputed.
2. Do the imputation of missing values.
3. Return df_imputed.
"""
        )

    def generate_features(self) -> DataFrameType:
        """
        Do feature generation and return the dataframe.

        Returns:
            DataFrameType: The DataFrame with generated features.
        """

        return self.chat(
            """
1. Copy the dataframe to a new variable named df_features.
2. Do feature generation.
3. Return df_features.
"""
        )

    def plot_pie_chart(self, labels: list, values: list) -> None:
        """
        Plot a pie chart.

        Args:
            labels (list): The labels for the pie chart.
            values (list): The values for the pie chart.

        Returns:
            None
        """

        self.chat(
            f"""
Plot a pie chart with the following labels and values:
labels = {labels}
values = {values}
"""
        )

    def plot_bar_chart(self, x: list, y: list) -> None:
        """
        Plot a bar chart.

        Args:
            x (list): The x values for the bar chart.
            y (list): The y values for the bar chart.

        Returns:
            None
        """

        self.chat(
            f"""
Plot a bar chart with the following x and y:
x = {x}
y = {y}
"""
        )

    def plot_histogram(self, column: str) -> None:
        """
        Plot a histogram.

        Args:
            column (str): The column to plot the histogram for.

        Returns:
            None
        """

        self.chat(f"Plot a histogram of the column {column}.")

    def plot_line_chart(self, x: list, y: list) -> None:
        """
        Plot a line chart.

        Args:
            x (list): The x values for the line chart.
            y (list): The y values for the line chart.

        Returns:
            None
        """

        self.chat(
            f"""
Plot a line chart with the following x and y:
x = {x}
y = {y}
"""
        )

    def plot_scatter_chart(self, x: list, y: list) -> None:
        """
        Plot a scatter chart.

        Args:
            x (list): The x values for the scatter chart.
            y (list): The y values for the scatter chart.

        Returns:
            None
        """

        self.chat(
            f"""
Plot a scatter chart with the following x and y:
x = {x}
y = {y}
"""
        )

    def plot_correlation_heatmap(self) -> None:
        """
        Plot a correlation heatmap.

        Returns:
            None
        """

        self.chat("Plot a correlation heatmap.")

    def plot_confusion_matrix(self, y_true: list, y_pred: list) -> None:
        """
        Plot a confusion matrix.

        Args:
            y_true (list): The true values.
            y_pred (list): The predicted values.

        Returns:
            None
        """

        self.chat(
            f"""
Plot a confusion matrix with the following y_true and y_pred:
y_true = {y_true}
y_pred = {y_pred}
"""
        )

    def plot_roc_curve(self, y_true: list, y_pred: list) -> None:
        """
        Plot a ROC curve.

        Args:
            y_true (list): The true values.
            y_pred (list): The predicted values.

        Returns:
            None
        """

        self.chat(
            f"""
Plot a ROC curve with the following y_true and y_pred:
y_true = {y_true}
y_pred = {y_pred}
"""
        )

    def boxplot(
        self,
        col: Union[str, list[str]] = None,
        by: Union[str, list[str]] = None,
        style: str = None,
    ):
        """
        Draw a box plot to show distributions with respect to categories.

        Args:
            col (str | list[str] | None): The column(s) of interest
            for the box plot. Defaults to None.
            by (str | list[str] | None): The grouping variable(s)
            for the box plot. Defaults to None.
            style (str | None): The textual description of the desired
            style. Defaults to None.

        Returns:
            str: LLM response.

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

        self.chat(prompt)

    def rolling_mean(self, column: str, window: int) -> DataFrameType:
        """
        Calculate the rolling mean.

        Args:
            column (str): The column to calculate the rolling mean for.
            window (int): The window size.

        Returns:
            DataFrameType: The DataFrame containing the rolling mean.
        """

        return self.chat(
            f"Calculate the rolling mean of the column {column} with a window"
            f" of {window}.",
        )

    def rolling_median(self, column: str, window: int) -> DataFrameType:
        """
        Calculate the rolling median.

        Args:
            column (str): The column to calculate the rolling median for.
            window (int): The window size.

        Returns:
            DataFrameType: The DataFrame containing the rolling median.
        """

        return self.chat(
            f"Calculate the rolling median of the column {column} with a window"
            f" of {window}.",
        )

    def rolling_std(self, column: str, window: int) -> DataFrameType:
        """
        Calculate the rolling standard deviation.

        Args:
            column (str): The column to calculate the rolling standard deviation for.
            window (int): The window size.

        Returns:
            DataFrameType: The DataFrame containing the rolling standard deviation.
        """

        return self.chat(
            f"Calculate the rolling standard deviation of the column {column} with a"
            f"window of {window}.",
        )

    def segment_customers(self, features: list, n_clusters: int) -> DataFrameType:
        """
        Segment customers.

        Args:
            features (list): The features to use for the segmentation.
            n_clusters (int): The number of clusters.

        Returns:
            DataFrameType: The DataFrame containing the segmentation.
        """

        return self.chat(
            f"""
Segment customers with the following features and number of clusters:
features = {features}
n_clusters = {n_clusters}
"""
        )
