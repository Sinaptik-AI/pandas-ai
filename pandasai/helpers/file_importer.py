import pandasai.pandas as pd

from .from_google_sheets import from_google_sheets


class FileImporter:
    """
    Class to import a dataframe from a file (csv, parquet, xlsx)
    """

    @staticmethod
    def import_from_file(file_path: str) -> pd.DataFrame:
        """
        Import a dataframe from a file (csv, parquet, xlsx)

        Args:
            file_path (str): Path to the file to be imported.

        Returns:
            pd.DataFrame: Pandas dataframe
        """

        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".parquet"):
            return pd.read_parquet(file_path)
        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)
        elif file_path.startswith("https://docs.google.com/spreadsheets/"):
            return from_google_sheets(file_path)[0]
        else:
            raise ValueError("Invalid file format.")
