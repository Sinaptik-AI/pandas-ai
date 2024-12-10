from importlib.util import find_spec
import json
import os

import pandasai.llm as llm
from pandasai.llm.base import LLM

from .helpers.path import find_closest

from typing import Any, List, Optional, Dict, Union
from pydantic import BaseModel, Field, ConfigDict

from pandasai.constants import DEFAULT_CHART_DIRECTORY


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    use_error_correction_framework: bool = True
    save_charts: bool = False
    save_charts_path: str = DEFAULT_CHART_DIRECTORY
    custom_whitelisted_dependencies: List[str] = Field(default_factory=list)
    max_retries: int = 3

    llm: Optional[LLM] = None
    data_viz_library: Optional[str] = None
    direct_sql: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Config":
        return cls(**config)

    # @model_validator(mode="before")
    # def on_llm_change(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     This method is triggered when the model is being validated.
    #     If 'llm' is passed, it ensures it's correctly set.
    #     """
    #     if "llm" in values or cls.llm == None:
    #         llm_value = values.get("llm")
    #         if llm_value is None:
    #             # If no LLM is provided, initialize based on environment variable
    #             llm_value = cls.run_on_llm_change(llm_value)
    #         values["llm"] = (
    #             llm_value  # Update the values dictionary with the final LLM value
    #         )
    #     return values

    # @staticmethod
    # def run_on_llm_change(llm_value: Optional[LLM] = None) -> Optional[LLM]:
    #     """
    #     Initializes a default LLM if not provided.
    #     """
    #     if llm_value is None and os.environ.get("PANDASAI_API_KEY"):
    #         from pandasai.llm.bamboo_llm import BambooLLM

    #         return BambooLLM()

    #     # Check if pandasai_langchain is installed
    #     if find_spec("pandasai_langchain") is not None:
    #         from pandasai_langchain.langchain import LangchainLLM, is_langchain_llm

    #         if is_langchain_llm(llm_value):
    #             return LangchainLLM(llm_value)

    #     return llm_value


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

            # if config is a dict
            if config.get("llm") and not override_config.get("llm"):
                options = config.get("llm_options") or {}
                config["llm"] = getattr(llm, config["llm"])(**options)
            elif not config.get("llm") and not override_config.get("llm"):
                config["llm"] = llm.BambooLLM()
    except FileNotFoundError:
        # Ignore the error if the file does not exist, will use the default config
        pass

    if override_config:
        config.update(override_config)

    return config
