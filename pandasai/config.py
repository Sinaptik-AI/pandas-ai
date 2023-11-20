import json
from typing import Optional, Union

from . import llm
from .helpers.path import find_closest
from .schemas.df_config import Config


def load_config(
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
    except FileNotFoundError:
        # Ignore the error if the file does not exist, will use the default config
        pass

    if override_config:
        config.update(override_config)

    return config
