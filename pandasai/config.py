import json
from . import llm, middlewares, callbacks
from .helpers.path import find_closest
from .schemas.df_config import Config


def load_config(override_config: Config = None):
    config = {}

    if override_config is None:
        override_config = {}

    try:
        with open(find_closest("pandasai.json"), "r") as f:
            config = json.load(f)

            if config.get("llm") and not override_config.get("llm"):
                options = config.get("llm_options") or {}
                config["llm"] = getattr(llm, config["llm"])(**options)

            if config.get("middlewares") and not override_config.get("middlewares"):
                config["middlewares"] = [
                    getattr(middlewares, middleware)()
                    for middleware in config["middlewares"]
                ]

            if config.get("callback") and not override_config.get("callback"):
                config["callback"] = getattr(callbacks, config["callback"])()
    except Exception:
        pass

    if override_config:
        config.update(override_config)

    return config
