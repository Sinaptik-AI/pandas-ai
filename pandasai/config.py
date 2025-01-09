import json
import os
from importlib.util import find_spec
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

import pandasai.llm as llm
from pandasai.constants import DEFAULT_CHART_DIRECTORY
from pandasai.llm.base import LLM

from .helpers.path import find_closest


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enable_cache: bool = True
    save_charts: bool = False
    save_charts_path: str = DEFAULT_CHART_DIRECTORY
    custom_whitelisted_dependencies: List[str] = Field(default_factory=list)
    max_retries: int = 3
    llm: Optional[LLM] = None
    direct_sql: bool = False
    security: Literal["standard", "none", "advanced"] = "standard"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Config":
        return cls(**config)


class ConfigManager:
    """A singleton class to manage the global configuration."""

    _config: Config = Config()

    @classmethod
    def set(cls, config_dict: Dict[str, Any]) -> None:
        """Set the global configuration."""
        cls._config = Config.from_dict(config_dict)
        cls.validate_llm()

    @classmethod
    def get(cls) -> Config:
        """Get the global configuration."""
        if cls._config.llm is None and os.environ.get("PANDASAI_API_KEY"):
            from pandasai.llm.bamboo_llm import BambooLLM

            cls._config.llm = BambooLLM()

        return cls._config

    @classmethod
    def update(cls, config_dict: Dict[str, Any]) -> None:
        """Update the existing configuration with new values."""
        current_config = cls._config.model_dump()
        current_config.update(config_dict)
        cls._config = Config.from_dict(current_config)

    @classmethod
    def validate_llm(cls):
        """
        Initializes a default LLM if not provided.
        """
        if cls._config.llm is None and os.environ.get("PANDASAI_API_KEY"):
            from pandasai.llm.bamboo_llm import BambooLLM

            cls._config.llm = BambooLLM()
            return

        # Check if pandasai_langchain is installed
        if find_spec("pandasai_langchain") is not None:
            from pandasai_langchain.langchain import LangchainLLM, is_langchain_llm

            if is_langchain_llm(cls._config.llm):
                cls._config.llm = LangchainLLM(cls._config.llm)


class APIKeyManager:
    _api_key: Optional[str] = None

    @classmethod
    def set(cls, api_key: str):
        os.environ["PANDASAI_API_KEY"] = api_key
        cls._api_key = api_key

    @classmethod
    def get(cls) -> Optional[str]:
        return cls._api_key


def load_config_from_json(
    override_config: Optional[Union[Config, dict]] = None,
):
    """
    Load the configuration from the pandasai.json file.

    Args:
        override_config (Optional[Union[Config, dict]], optional): The configuration to
        override the one in the file. Defaults to None.

    Returns:
        dict: The configuration.
    """

    config = {}

    if override_config is None:
        override_config = {}

    if isinstance(override_config, Config):
        override_config = override_config.dict()

    try:
        with open(find_closest("pandasai.json"), "r") as f:
            config = json.load(f)

            if not config.get("llm") and not override_config.get("llm"):
                config["llm"] = llm.BambooLLM()
    except FileNotFoundError:
        # Ignore the error if the file does not exist, will use the default config
        pass

    if override_config:
        config.update(override_config)

    return config
