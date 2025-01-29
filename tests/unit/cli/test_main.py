from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from pandasai.cli.main import cli, get_validated_dataset_path


def test_get_validated_dataset_path_valid():
    """Test get_validated_dataset_path with valid input"""
    org, dataset = get_validated_dataset_path("my-org/my-dataset")
    assert org == "my-org"
    assert dataset == "my-dataset"


def test_get_validated_dataset_path_invalid_format():
    """Test get_validated_dataset_path with invalid format"""
    with pytest.raises(
        ValueError, match="Path must be in format: organization/dataset"
    ):
        get_validated_dataset_path("invalid-path")


def test_get_validated_dataset_path_invalid_org():
    """Test get_validated_dataset_path with invalid organization name"""
    with pytest.raises(
        ValueError, match="Organization name must be lowercase with hyphens"
    ):
        get_validated_dataset_path("INVALID_ORG/dataset")


def test_get_validated_dataset_path_invalid_dataset():
    """Test get_validated_dataset_path with invalid dataset name"""
    with pytest.raises(ValueError, match="Dataset name must be lowercase with hyphens"):
        get_validated_dataset_path("my-org/INVALID_DATASET")


@pytest.fixture
def mock_dataset_loader():
    with patch("pandasai.cli.main.DatasetLoader") as mock:
        yield mock


@pytest.fixture
def mock_project_root(tmp_path):
    datasets_dir = tmp_path / "datasets"
    datasets_dir.mkdir()
    with patch("pandasai.cli.main.find_project_root") as mock:
        mock.return_value = str(tmp_path)
        yield mock


@patch("pandasai.cli.main.SemanticLayerSchema")
def test_dataset_create_command(mock_schema, mock_project_root, tmp_path):
    """Test dataset create command with valid input"""
    runner = CliRunner()

    # Mock schema instance
    mock_schema_instance = MagicMock()
    mock_schema_instance.to_yaml.return_value = "mock yaml content"
    mock_schema.return_value = mock_schema_instance

    # Mock user input
    inputs = [
        "test-org/test-dataset\n",  # dataset path
        "\n",  # dataset name (default)
        "\n",  # description (empty)
        "\n",  # source type (default: mysql)
        "users\n",  # table name
        "\n",  # host (default: localhost)
        "3306\n",  # port
        "testdb\n",  # database name
        "testuser\n",  # username
        "testpass\n",  # password
    ]

    result = runner.invoke(cli, ["dataset", "create"], input="".join(inputs))
    assert result.exit_code == 0
    assert "✨ Dataset created successfully" in result.output

    # Verify directory and file were created
    dataset_dir = tmp_path / "datasets" / "test-org" / "test-dataset"
    assert dataset_dir.exists()
    assert (dataset_dir / "schema.yaml").exists()


@patch("pandasai.cli.main.SemanticLayerSchema")
def test_dataset_create_existing(mock_schema, mock_project_root, tmp_path):
    """Test dataset create command when dataset already exists"""
    runner = CliRunner()

    # Create dataset directory and schema file
    dataset_dir = tmp_path / "datasets" / "test-org" / "test-dataset"
    dataset_dir.mkdir(parents=True)
    schema_file = dataset_dir / "schema.yaml"
    schema_file.write_text("test content")

    result = runner.invoke(cli, ["dataset", "create"], input="test-org/test-dataset\n")
    assert result.exit_code == 0
    assert "Error: Dataset already exists" in result.output


def test_pull_command(mock_dataset_loader):
    """Test pull command"""
    runner = CliRunner()
    mock_df = MagicMock()
    mock_dataset_loader.return_value.load.return_value = mock_df

    result = runner.invoke(cli, ["pull", "test-org/test-dataset"])

    assert result.exit_code == 0
    mock_dataset_loader.return_value.load.assert_called_once_with(
        "test-org/test-dataset"
    )
    mock_df.pull.assert_called_once()
    assert "✨ Dataset successfully pulled" in result.output


def test_push_command(mock_dataset_loader):
    """Test push command"""
    runner = CliRunner()
    mock_df = MagicMock()
    mock_dataset_loader.return_value.load.return_value = mock_df

    result = runner.invoke(cli, ["push", "test-org/test-dataset"])

    assert result.exit_code == 0
    mock_dataset_loader.return_value.load.assert_called_once_with(
        "test-org/test-dataset"
    )
    mock_df.push.assert_called_once()
    assert "✨ Dataset successfully pushed" in result.output


def test_pull_command_error(mock_dataset_loader):
    """Test pull command with error"""
    runner = CliRunner()
    mock_dataset_loader.return_value.load.side_effect = Exception("Test error")

    result = runner.invoke(cli, ["pull", "test-org/test-dataset"])

    assert result.exit_code == 0  # CLI handles the error gracefully
    assert "Error pulling dataset: Test error" in result.output


def test_push_command_error(mock_dataset_loader):
    """Test push command with error"""
    runner = CliRunner()
    mock_dataset_loader.return_value.load.side_effect = Exception("Test error")

    result = runner.invoke(cli, ["push", "test-org/test-dataset"])

    assert result.exit_code == 0  # CLI handles the error gracefully
    assert "Error pushing dataset: Test error" in result.output
