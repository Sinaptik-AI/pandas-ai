import os
from unittest.mock import MagicMock, patch

from pandasai.config import Config, ConfigManager
from pandasai.helpers.filemanager import DefaultFileManager
from pandasai.llm.bamboo_llm import BambooLLM


def test_validate_llm_with_pandabi_api_key():
    # Setup
    ConfigManager._config = MagicMock()
    ConfigManager._config.llm = None

    with patch.dict(os.environ, {"PANDABI_API_KEY": "test-key"}):
        # Execute
        ConfigManager.validate_llm()

        # Assert
        assert isinstance(ConfigManager._config.llm, BambooLLM)


def test_validate_llm_with_langchain():
    # Setup
    ConfigManager._config = MagicMock()
    mock_llm = MagicMock()
    ConfigManager._config.llm = mock_llm
    mock_langchain_llm = MagicMock()

    # Create mock module
    mock_langchain_module = MagicMock()
    mock_langchain_module.__spec__ = MagicMock()
    mock_langchain_module.langchain = MagicMock(
        LangchainLLM=mock_langchain_llm, is_langchain_llm=lambda x: True
    )

    with patch.dict(
        "sys.modules",
        {
            "pandasai_langchain": mock_langchain_module,
            "pandasai_langchain.langchain": mock_langchain_module.langchain,
        },
    ):
        # Execute
        ConfigManager.validate_llm()

        # Assert
        assert mock_langchain_llm.call_count == 1


def test_validate_llm_no_action_needed():
    # Setup
    ConfigManager._config = MagicMock()
    mock_llm = MagicMock()
    ConfigManager._config.llm = mock_llm

    # Case where no PANDABI_API_KEY and not a langchain LLM
    with patch.dict(os.environ, {}, clear=True):
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = None

            # Execute
            ConfigManager.validate_llm()

            # Assert - llm should remain unchanged
            assert ConfigManager._config.llm == mock_llm


def test_config_update():
    # Setup
    mock_config = MagicMock()
    initial_config = {"key1": "value1", "key2": "value2"}
    mock_config.model_dump = MagicMock(return_value=initial_config.copy())
    ConfigManager._config = mock_config

    # Create a mock for Config.from_dict
    original_from_dict = Config.from_dict
    Config.from_dict = MagicMock()

    try:
        # Execute
        new_config = {"key2": "new_value2", "key3": "value3"}
        ConfigManager.update(new_config)

        # Assert
        expected_config = {"key1": "value1", "key2": "new_value2", "key3": "value3"}
        assert mock_config.model_dump.call_count == 1
        Config.from_dict.assert_called_once_with(expected_config)
    finally:
        # Restore original from_dict method
        Config.from_dict = original_from_dict


def test_config_set():
    # Setup
    test_config = {"key": "value"}
    with patch.object(Config, "from_dict") as mock_from_dict, patch.object(
        ConfigManager, "validate_llm"
    ) as mock_validate_llm:
        # Execute
        ConfigManager.set(test_config)

        # Assert
        mock_from_dict.assert_called_once_with(test_config)
        mock_validate_llm.assert_called_once()


def test_config_from_dict():
    # Test with default overrides
    config_dict = {
        "save_logs": False,
        "verbose": True,
        "enable_cache": False,
        "max_retries": 5,
    }

    config = Config.from_dict(config_dict)

    assert isinstance(config, Config)
    assert config.save_logs == False
    assert config.verbose == True
    assert config.enable_cache == False
    assert config.max_retries == 5
    assert config.llm is None
    assert isinstance(config.file_manager, DefaultFileManager)

    # Test with minimal dict
    minimal_config = Config.from_dict({})
    assert isinstance(minimal_config, Config)
    assert minimal_config.save_logs == True  # default value
    assert minimal_config.verbose == False  # default value
    assert minimal_config.enable_cache == True  # default value
    assert minimal_config.max_retries == 3  # default value
