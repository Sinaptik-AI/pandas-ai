import io
import os
import zipfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

import pandasai
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import DatasetNotFound, PandaAIApiKeyError


def create_test_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("test.csv", "a,b,c\n1,2,3")
    return zip_buffer.getvalue()


class TestPandaAIInit:
    @pytest.fixture
    def sample_df(self):
        return DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    @pytest.fixture
    def sample_dataframes(self):
        df1 = DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        df2 = DataFrame({"X": [10, 20, 30], "Y": ["x", "y", "z"]})
        return [df1, df2]

    @pytest.fixture
    def sample_schema(self):
        from pandasai.data_loader.semantic_layer_schema import (
            Column,
            SemanticLayerSchema,
            Source,
        )

        return SemanticLayerSchema(
            name="test_dataset",
            description="A test dataset",
            source=Source(type="parquet", path="data.parquet"),
            columns=[
                Column(name="A", type="integer", description="Column A"),
                Column(name="B", type="integer", description="Column B"),
            ],
        )

    def test_chat_creates_agent(self, sample_df):
        with patch("pandasai.Agent") as MockAgent:
            pandasai.chat("Test query", sample_df)
            MockAgent.assert_called_once_with([sample_df])

    def test_chat_without_dataframes_raises_error(self):
        with pytest.raises(ValueError, match="At least one dataframe must be provided"):
            pandasai.chat("Test query")

    def test_follow_up_without_chat_raises_error(self):
        pandasai._current_agent = None
        with pytest.raises(ValueError, match="No existing conversation"):
            pandasai.follow_up("Follow-up query")

    def test_follow_up_after_chat(self, sample_df):
        with patch("pandasai.Agent") as MockAgent:
            mock_agent = MockAgent.return_value
            pandasai.chat("Test query", sample_df)
            pandasai.follow_up("Follow-up query")
            mock_agent.follow_up.assert_called_once_with("Follow-up query")

    def test_chat_with_multiple_dataframes(self, sample_dataframes):
        with patch("pandasai.Agent") as MockAgent:
            mock_agent_instance = MagicMock()
            MockAgent.return_value = mock_agent_instance
            mock_agent_instance.chat.return_value = "Mocked response"

            result = pandasai.chat("What is the sum of column A?", *sample_dataframes)

            MockAgent.assert_called_once_with(sample_dataframes)
            mock_agent_instance.chat.assert_called_once_with(
                "What is the sum of column A?"
            )
            assert result == "Mocked response"

    def test_chat_with_single_dataframe(self, sample_dataframes):
        with patch("pandasai.Agent") as MockAgent:
            mock_agent_instance = MagicMock()
            MockAgent.return_value = mock_agent_instance
            mock_agent_instance.chat.return_value = "Mocked response"

            result = pandasai.chat(
                "What is the average of column X?", sample_dataframes[1]
            )

            MockAgent.assert_called_once_with([sample_dataframes[1]])
            mock_agent_instance.chat.assert_called_once_with(
                "What is the average of column X?"
            )
            assert result == "Mocked response"

    @patch("pandasai.data_loader.loader.DatasetLoader")
    @patch("pandasai.helpers.path.find_project_root")
    @patch("os.path.exists")
    def test_load_valid_dataset(
        self, mock_exists, mock_find_project_root, mock_dataset_loader
    ):
        """Test loading a valid dataset."""
        mock_find_project_root.return_value = "/mock/root"
        mock_dataset_loader.load.return_value = MagicMock(name="DataFrame")
        mock_exists.return_value = True
        pandasai._dataset_loader = mock_dataset_loader

        dataset_path = "org/dataset_name"
        result = pandasai.load(dataset_path)

        mock_dataset_loader.load.assert_called_once_with(dataset_path)
        assert isinstance(result, MagicMock)

    @patch("zipfile.ZipFile")
    @patch("io.BytesIO")
    @patch("os.environ")
    def test_load_dataset_not_found(self, mockenviron, mock_bytes_io, mock_zip_file):
        """Test loading when dataset does not exist locally and API returns not found."""
        mockenviron.return_value = {"PANDABI_API_URL": "localhost:8000"}
        mock_request_session = MagicMock()
        pandasai.get_pandaai_session = mock_request_session
        pandasai.get_pandaai_session.return_value = MagicMock()
        mock_request_session.get.return_value.status_code = 404

        dataset_path = "org/dataset_name"

        with pytest.raises(DatasetNotFound):
            pandasai.load(dataset_path)

    @patch("pandasai.os.path.exists")
    @patch("pandasai.os.environ", {"PANDABI_API_KEY": "key"})
    def test_load_missing_api_url(self, mock_exists):
        """Test loading when API URL is missing."""
        mock_exists.return_value = False
        dataset_path = "org/dataset_name"

        with pytest.raises(PandaAIApiKeyError):
            pandasai.load(dataset_path)

    @patch("pandasai.os.path.exists")
    @patch("pandasai.os.environ", {"PANDABI_API_KEY": "key"})
    @patch("pandasai.get_pandaai_session")
    def test_load_missing_api_url(self, mock_session, mock_exists):
        """Test loading when API URL is missing."""
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.return_value.get.return_value = mock_response
        dataset_path = "org/dataset_name"

        with pytest.raises(DatasetNotFound):
            pandasai.load(dataset_path)

    @patch("pandasai.os.environ", new_callable=dict)
    @patch("pandasai.os.path.exists")
    @patch("pandasai.get_pandaai_session")
    @patch("pandasai.ZipFile")
    @patch("pandasai.BytesIO")
    @patch("pandasai.data_loader.loader.DatasetLoader")
    def test_load_successful_zip_extraction(
        self,
        mock_dataset_loader,
        mock_bytes_io,
        mock_zip_file,
        mock_get_pandaai_session,
        mock_exists,
        mock_os_environ,
    ):
        """Test loading when dataset is not found locally but is successfully downloaded."""
        mock_exists.return_value = False
        mock_os_environ.update({"PANDABI_API_KEY": "key", "PANDABI_API_URL": "url"})
        mock_request_session = MagicMock()
        mock_get_pandaai_session.return_value = mock_request_session
        mock_request_session.get.return_value.status_code = 200
        mock_request_session.get.return_value.content = b"mock zip content"
        pandasai._dataset_loader = mock_dataset_loader

        dataset_path = "org/dataset_name"

        # Mock the zip file extraction
        mock_zip_file.return_value.__enter__.return_value.extractall = MagicMock()

        result = pandasai.load(dataset_path)

        mock_zip_file.return_value.__enter__.return_value.extractall.assert_called_once()
        assert isinstance(result, MagicMock)

    def test_load_without_api_credentials(self):
        """Test that load raises PandaAIApiKeyError when no API credentials are provided"""
        with pytest.raises(PandaAIApiKeyError) as exc_info:
            pandasai.load("test/dataset")
        assert (
            str(exc_info.value)
            == "PandaAI API key not found. Please set your API key using PandaAI.set_api_key() or by setting the PANDASAI_API_KEY environment variable."
        )

    def test_clear_cache(self):
        with patch("pandasai.core.cache.Cache.clear") as mock_clear:
            pandasai.clear_cache()
            mock_clear.assert_called_once()

    @patch.dict(os.environ, {"PANDABI_API_KEY": "test-key"})
    @patch("pandasai.get_pandaai_session")
    @patch("pandasai.os.path.exists")
    @patch("pandasai.helpers.path.find_project_root")
    @patch("pandasai.os.makedirs")
    def test_load_with_default_api_url(
        self, mock_makedirs, mock_root, mock_exists, mock_session
    ):
        """Test that load uses DEFAULT_API_URL when no URL is provided"""
        mock_root.return_value = "/tmp/test_project"
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = create_test_zip()
        mock_session.return_value.get.return_value = mock_response

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("zipfile.ZipFile") as mock_zip_file:
                mock_zip_file.return_value.__enter__.return_value.extractall = (
                    MagicMock()
                )
                pandasai.load("org/dataset")

        mock_session.return_value.get.assert_called_once_with(
            "/datasets/pull",
            headers={
                "accept": "application/json",
                "x-authorization": "Bearer test-key",
            },
            params={"path": "org/dataset"},
        )

    @patch.dict(
        os.environ,
        {"PANDABI_API_KEY": "test-key", "PANDABI_API_URL": "https://custom.api.url"},
    )
    @patch("pandasai.get_pandaai_session")
    @patch("pandasai.os.path.exists")
    @patch("pandasai.helpers.path.find_project_root")
    @patch("pandasai.os.makedirs")
    def test_load_with_custom_api_url(
        self, mock_makedirs, mock_root, mock_exists, mock_session
    ):
        """Test that load uses custom URL from environment"""
        mock_root.return_value = "/tmp/test_project"
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = create_test_zip()
        mock_session.return_value.get.return_value = mock_response

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("zipfile.ZipFile") as mock_zip_file:
                mock_zip_file.return_value.__enter__.return_value.extractall = (
                    MagicMock()
                )
                pandasai.load("org/dataset")

        mock_session.return_value.get.assert_called_once_with(
            "/datasets/pull",
            headers={
                "accept": "application/json",
                "x-authorization": "Bearer test-key",
            },
            params={"path": "org/dataset"},
        )

    @patch("pandasai.helpers.path.find_project_root")
    @patch("os.makedirs")
    def test_create_valid_dataset(
        self, mock_makedirs, mock_find_project_root, sample_df, sample_schema
    ):
        """Test creating a dataset with valid inputs."""
        mock_find_project_root.return_value = "/mock/root"

        with patch("builtins.open", mock_open()) as mock_file, patch.object(
            sample_df, "to_parquet"
        ) as mock_to_parquet, patch(
            "pandasai.find_project_root", return_value="/mock/root"
        ):
            result = pandasai.create("test-org/test-dataset", sample_df, sample_schema)

            # Check if directories were created
            mock_makedirs.assert_called_once_with(
                "/mock/root/datasets/test-org/test-dataset", exist_ok=True
            )

            # Check if DataFrame was saved
            mock_to_parquet.assert_called_once()
            assert mock_to_parquet.call_args[0][0].endswith("data.parquet")
            assert mock_to_parquet.call_args[1]["index"] is False

            # Check if schema was saved
            mock_file.assert_called_once_with(
                "/mock/root/datasets/test-org/test-dataset/schema.yaml", "w"
            )

            # Check returned DataFrame
            assert isinstance(result, DataFrame)
            assert result.name == sample_schema.name
            assert result.description == sample_schema.description
            assert result.path == "test-org/test-dataset"

    def test_create_invalid_path_format(self, sample_df, sample_schema):
        """Test creating a dataset with invalid path format."""
        with pytest.raises(
            ValueError, match="Path must be in format 'organization/dataset'"
        ):
            pandasai.create("invalid_path", sample_df, sample_schema)

    def test_create_invalid_org_name(self, sample_df, sample_schema):
        """Test creating a dataset with invalid organization name."""
        with pytest.raises(ValueError, match="Organization name must be lowercase"):
            pandasai.create("Invalid-Org/test-dataset", sample_df, sample_schema)

    def test_create_invalid_dataset_name(self, sample_df, sample_schema):
        """Test creating a dataset with invalid dataset name."""
        with pytest.raises(ValueError, match="Dataset name must be lowercase"):
            pandasai.create("test-org/Invalid-Dataset", sample_df, sample_schema)

    def test_create_empty_org_name(self, sample_df, sample_schema):
        """Test creating a dataset with empty organization name."""
        with pytest.raises(
            ValueError, match="Both organization and dataset names are required"
        ):
            pandasai.create("/test-dataset", sample_df, sample_schema)

    def test_create_empty_dataset_name(self, sample_df, sample_schema):
        """Test creating a dataset with empty dataset name."""
        with pytest.raises(
            ValueError, match="Both organization and dataset names are required"
        ):
            pandasai.create("test-org/", sample_df, sample_schema)
