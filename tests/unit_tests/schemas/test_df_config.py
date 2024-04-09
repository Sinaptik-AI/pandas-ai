import os

from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.schemas.df_config import Config


def test_config_llm_default_type() -> None:
    # Define a mock environment for testing
    os.environ["PANDASAI_API_URL"] = "http://test-server"
    os.environ["PANDASAI_API_KEY"] = "test-api-key"

    # Create an instance of Config without any arguments
    config = Config()

    # Assert that the llm attribute is an instance of the expected default type (BambooLLM)
    assert isinstance(
        config.llm, BambooLLM
    ), "Default LLM type should be BambooLLM when Config is instantiated without arguments."
