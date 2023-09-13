"""
Class to manage the configuration of the dataframe
"""

import json
import os
import hashlib
from pandasai.helpers.path import create_directory, find_closest, find_project_root
from .df_info import df_type


class DfConfigManager:
    """
    Class to manage the configuration of the dataframe
    """

    _sdf = None

    def __init__(self, sdf):
        """
        Args:
            sdf (SmartDataframe): SmartDataframe object
        """

        from ..smart_dataframe import SmartDataframe

        if isinstance(sdf, SmartDataframe):
            self._sdf = sdf
        else:
            raise TypeError("Expected instance of type 'SmartDataFrame'")

    def _create_csv_save_path(self):
        """
        Creates the path for the csv file to be saved
        """

        directory_path = os.path.join(find_project_root(), "cache")
        create_directory(directory_path)
        csv_file_path = os.path.join(directory_path, f"{self._sdf.table_name}.csv")
        return csv_file_path

    def _check_for_duplicates(self, saved_dfs):
        """
        Checks if the dataframe name already exists

        Args:
            saved_dfs (List[dict]): List of saved dataframes
        """

        if any(df_info["name"] == self._sdf.table_name for df_info in saved_dfs):
            raise ValueError(f"Duplicate dataframe found: {self._sdf.table_name}")

    def _get_import_path(self):
        """
        Gets the import path for the dataframe
        """

        # Handle connectors
        if self._sdf.connector is not None:
            return self._sdf.connector.path

        # Return if already a string
        if isinstance(self.original_import, str):
            # Check if it is a csv or xlsx file
            if (
                self.original_import.endswith(".csv")
                or self.original_import.endswith(".parquet")
                or self.original_import.endswith(".xlsx")
                or self.original_import.startswith(
                    "https://docs.google.com/spreadsheets/"
                )
            ):
                return self.original_import

            # Otherwise, it means it is a dataframe imported from config
            raise ValueError("Dataframe imported from config cannot be saved")

        # Save df if pandas or polar
        dataframe_type = df_type(self.original_import)
        if dataframe_type == "pandas":
            csv_file_path = self._create_csv_save_path()
            self._sdf.dataframe.to_csv(csv_file_path)
        elif dataframe_type == "polars":
            csv_file_path = self._create_csv_save_path()
            with open(csv_file_path, "w") as f:
                self._sdf.dataframe.write_csv(f)
        else:
            raise ValueError("Unknown dataframe type")

        return csv_file_path

    def save(self, name=None):
        """
        Saves the dataframe object to used for later

        Args:
            name (str, optional): Name of the dataframe. Defaults to None.

        Raises:
            ValueError: If the dataframe name already exists
        """

        file_path = find_closest("pandasai.json")

        # Open config file
        saved_df_keys = "saved_dfs"
        with open(file_path, "r+") as json_file:
            pandas_json = json.load(json_file)
            if saved_df_keys not in pandas_json:
                pandas_json[saved_df_keys] = []

            # Check for duplicates
            self._check_for_duplicates(pandas_json[saved_df_keys])

            # Get import path
            import_path = self._get_import_path()

            pandas_json[saved_df_keys].append(
                {
                    "name": name if name is not None else self.name,
                    "description": self._sdf.table_description,
                    "sample": self._sdf.head_csv,
                    "import_path": import_path,
                }
            )

            json_file.seek(0)
            json.dump(pandas_json, json_file, indent=2)
            json_file.truncate()

    def load(self, name) -> dict:
        """
        Loads a dataframe from the config file

        Args:
            name (str): Name of the dataframe

        Returns:
            dict: Dictionary with dataframe information
        """
        file_path = find_closest("pandasai.json")

        with open(file_path, "r") as json_file:
            pandas_json = json.load(json_file)
            self.saved_dfs = pandas_json["saved_dfs"]
            for df_info in self.saved_dfs:
                if df_info["name"] == name:
                    return df_info
        return {}

    @property
    def head_csv(self):
        return self._sdf.head_csv

    @property
    def name(self):
        name = self._sdf.table_name
        if name is None:
            # Generate random hash
            hash_object = hashlib.sha256(self._sdf.head_csv.encode())
            name = hash_object.hexdigest()
        return name

    @property
    def description(self):
        return self._sdf.table_description

    @property
    def original_import(self):
        return self._sdf._original_import
