import os
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest

import pandasai
from pandasai import find_project_root
from pandasai.agent import Agent
from pandasai.dataframe.base import DataFrame


class TestDataFrame:
    @pytest.fixture(autouse=True)
    def reset_current_agent(self):
        pandasai._current_agent = None
        yield
        pandasai._current_agent = None

    @pytest.fixture
    def sample_data(self):
        return {
            "Name": ["John", "Emma", "Liam", "Olivia", "Noah"],
            "Age": [28, 35, 22, 31, 40],
            "City": ["New York", "London", "Paris", "Tokyo", "Sydney"],
            "Salary": [75000, 82000, 60000, 79000, 88000],
        }

    @pytest.fixture
    def sample_df(self, sample_data):
        return DataFrame(sample_data)

    def test_dataframe_initialization(self, sample_data, sample_df):
        assert isinstance(sample_df, DataFrame)
        assert isinstance(sample_df, pd.DataFrame)
        assert sample_df.equals(pd.DataFrame(sample_data))

    def test_dataframe_operations(self, sample_df):
        assert len(sample_df) == 5
        assert list(sample_df.columns) == ["Name", "Age", "City", "Salary"]
        assert sample_df["Salary"].mean() == 76800

    @patch("pandasai.agent.Agent")
    @patch("os.environ")
    def test_chat_creates_agent(self, mock_env, mock_agent, sample_data):
        sample_df = DataFrame(sample_data)
        mock_env.return_value = {"PANDABI_API_URL": "localhost:8000"}
        sample_df.chat("Test query")
        mock_agent.assert_called_once_with([sample_df], config=sample_df.config)

    @patch("pandasai.Agent")
    def test_chat_reuses_existing_agent(self, sample_df):
        mock_agent = Mock(spec=Agent)
        sample_df._agent = mock_agent

        sample_df.chat("First query")
        assert sample_df._agent is not None
        initial_agent = sample_df._agent
        sample_df.chat("Second query")
        assert sample_df._agent is initial_agent

    def test_follow_up_without_chat_raises_error(self, sample_df):
        with pytest.raises(ValueError, match="No existing conversation"):
            sample_df.follow_up("Follow-up query")

    def test_follow_up_after_chat(self, sample_df):
        mock_agent = Mock(spec=Agent)
        sample_df._agent = mock_agent

        sample_df.follow_up("Follow-up query")
        assert mock_agent.follow_up.call_count == 1

    def test_chat_method(self, sample_df):
        mock_agent = Mock(spec=Agent)
        sample_df._agent = mock_agent

        sample_df.chat("Test question")

        assert sample_df._agent is not None
        assert mock_agent.chat.call_count == 1

    def test_chat_with_config(self, sample_df):
        config = {"max_retries": 100}
        with patch("pandasai.agent.Agent") as mock_agent:
            sample_df.chat("Test query", config=config)
            mock_agent.assert_called_once_with([sample_df], config=sample_df.config)
        assert sample_df.config.max_retries == 100

    def test_column_hash(self, sample_df):
        assert hasattr(sample_df, "column_hash")
        assert isinstance(sample_df.column_hash, str)
        assert len(sample_df.column_hash) == 32  # MD5 hash length

    def test_save_creates_correct_schema(self, sample_df):
        path = "org-name/dataset-name"
        name = "Test Dataset"
        description = "This is a test dataset"
        columns = [
            {"name": "Name", "type": "string"},
            {"name": "Age", "type": "integer"},
        ]

        with (
            patch("os.makedirs"),
            patch("pandas.DataFrame.to_parquet"),
            patch("builtins.open", mock_open()) as mock_file,
            patch("yaml.dump") as mock_yaml_dump,
        ):
            sample_df.save(path, name, description, columns)

            expected_schema = {
                "name": name,
                "description": description,
                "columns": [
                    {"name": "Name", "type": "string"},
                    {"name": "Age", "type": "integer"},
                ],
                "destination": {
                    "format": "parquet",
                    "path": "data.parquet",
                    "type": "local",
                },
                "source": {
                    "path": "data.parquet",
                    "type": "parquet",
                },
            }

            mock_yaml_dump.assert_called_once_with(
                expected_schema, mock_file(), sort_keys=False
            )

    def test_save_creates_directory_and_files(self, sample_df):
        path = "org-name/dataset-name"
        name = "Test Dataset"
        description = "This is a test dataset"
        columns = [
            {"name": "Name", "type": "string"},
            {"name": "Age", "type": "integer"},
        ]

        with (
            patch("os.makedirs") as mock_makedirs,
            patch("pandas.DataFrame.to_parquet") as mock_to_parquet,
            patch("builtins.open", mock_open()) as mock_file,
            patch("yaml.dump") as mock_yaml_dump,
        ):
            sample_df.save(path, name, description, columns)

            root = find_project_root()

            dataset_directory = os.path.join(
                root, "datasets", "org-name", "dataset-name"
            )

            # Assert directory creation
            mock_makedirs.assert_called_once_with(dataset_directory, exist_ok=True)

            # Assert Parquet file creation
            mock_to_parquet.assert_called_once_with(
                os.path.join(dataset_directory, "data.parquet"), index=False
            )

            # Assert schema YAML creation
            schema_path = os.path.join(dataset_directory, "schema.yaml")
            mock_yaml_dump.assert_called_once()
            mock_file.assert_called_once_with(schema_path, "w")
