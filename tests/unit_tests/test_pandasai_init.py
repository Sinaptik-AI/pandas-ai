from unittest.mock import MagicMock, patch

import pytest

import pandasai
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import DatasetNotFound, PandasAIApiKeyError


class TestPandasAIInit:
    @pytest.fixture
    def sample_df(self):
        return DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    @pytest.fixture
    def sample_dataframes(self):
        df1 = DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
        df2 = DataFrame({"X": [10, 20, 30], "Y": ["x", "y", "z"]})
        return [df1, df2]

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

        mock_dataset_loader.load.assert_called_once_with(dataset_path, False)
        assert isinstance(result, MagicMock)

    @patch("zipfile.ZipFile")
    @patch("io.BytesIO")
    @patch("os.environ")
    def test_load_dataset_not_found(self, mockenviron, mock_bytes_io, mock_zip_file):
        """Test loading when dataset does not exist locally and API returns not found."""
        mockenviron.return_value = {"PANDASAI_API_URL": "localhost:8000"}
        mock_request_session = MagicMock()
        pandasai.get_pandaai_session = mock_request_session
        pandasai.get_pandaai_session.return_value = MagicMock()
        mock_request_session.get.return_value.status_code = 404

        dataset_path = "org/dataset_name"

        with pytest.raises(DatasetNotFound):
            pandasai.load(dataset_path)

    @patch("pandasai.os.path.exists")
    @patch("pandasai.os.environ", {"PANDASAI_API_URL": "url"})
    def test_load_missing_api_key(self, mock_exists):
        """Test loading when API key is missing."""
        mock_exists.return_value = False
        dataset_path = "org/dataset_name"

        with pytest.raises(PandasAIApiKeyError):
            pandasai.load(dataset_path)

    @patch("pandasai.os.path.exists")
    @patch("pandasai.os.environ", {"PANDASAI_API_KEY": "key"})
    def test_load_missing_api_url(self, mock_exists):
        """Test loading when API URL is missing."""
        mock_exists.return_value = False
        dataset_path = "org/dataset_name"

        with pytest.raises(PandasAIApiKeyError):
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
        mock_os_environ.update({"PANDASAI_API_KEY": "key", "PANDASAI_API_URL": "url"})
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

    def test_clear_cache(self):
        with patch("pandasai.core.cache.Cache.clear") as mock_clear:
            pandasai.clear_cache()
            mock_clear.assert_called_once()
