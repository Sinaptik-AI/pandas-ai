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

    _df = None

    def __init__(self, df):
        """
        Args:
            df (DataFrameType): Pandas or Polars dataframe
        """

        self._df = df

    def _create_csv_save_path(self):
        """
        Creates the path for the csv file to be saved
        """

        directory_path = os.path.join(find_project_root(), "cache")
        create_directory(directory_path)
        csv_file_path = os.path.join(directory_path, f"{self.name}.csv")
        return csv_file_path

    def _check_for_duplicates(self, saved_dfs):
        """
        Checks if the dataframe name already exists

        Args:
            saved_dfs (List[dict]): List of saved dataframes
        """

        # Check for duplicates
        for df_info in saved_dfs:
            if df_info["name"] == self.name:
                raise ValueError(f"Duplicate dataframe found: {self.name}")

    def _get_import_path(self):
        """
        Gets the import path for the dataframe
        """

        # Return if already a string
        if isinstance(self.original_import, str):
            # Check if it is a csv or xlsx file
            if self.original_import.endswith(".csv") or self.original_import.endswith(
                ".xlsx"
            ):
                return self.original_import

            # Otherwise, it means it is a dataframe imported from config
            raise ValueError("Dataframe imported from config cannot be saved")

        # Save df if pandas or polar
        dataframe_type = df_type(self.original_import)
        if dataframe_type == "pandas":
            csv_file_path = self._create_csv_save_path()
            self._df.original.to_csv(csv_file_path)
        elif dataframe_type == "polars":
            csv_file_path = self._create_csv_save_path()
            with open(csv_file_path, "w") as f:
                self._df.original.write_csv(f)
        else:
            raise ValueError("Unknown dataframe type")

        return csv_file_path

    def save(self):
        """
        Saves the dataframe object to used for later
        """

        file_path = find_closest("pandasai.json")

        # Open config file
        saved_df_keys = "saved_dfs"
        with open(file_path, "r") as json_file:
            pandas_json = json.load(json_file)
            if saved_df_keys not in pandas_json:
                pandas_json[saved_df_keys] = []

            # Check for duplicates
            self._check_for_duplicates(pandas_json[saved_df_keys])

            # Get import path
            import_path = self._get_import_path()

            pandas_json[saved_df_keys].append(
                {
                    "name": self.name,
                    "description": self.description,
                    "sample": self.head_csv,
                    "import_path": import_path,
                }
            )

        # Save the output in pandasai.json
        with open(file_path, "w") as json_file:
            json.dump(pandas_json, json_file, indent=2)

    @property
    def head_csv(self):
        return self._df.head_csv

    @property
    def name(self):
        name = self._df.name
        if name is None:
            # Generate random hash
            hash_object = hashlib.sha256(self.head_csv.encode())
            name = hash_object.hexdigest()
        return name

    @property
    def description(self):
        return self._df.description

    @property
    def original_import(self):
        return self._df.original_import
