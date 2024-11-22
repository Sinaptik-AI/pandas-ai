import json

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
