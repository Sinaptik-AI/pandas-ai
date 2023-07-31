import json
from pydantic import BaseModel
from typing import Union, List, Optional
from ..middlewares.base import Middleware
from ..callbacks.base import BaseCallback
from ..llm import LLM, LangchainLLM
from .. import llm, middlewares, callbacks


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    anonymize_dataframe: bool = True
    use_error_correction_framework: bool = True
    custom_prompts: dict = {}
    save_charts: bool = False
    save_charts_path: str = "exports/charts"
    custom_whitelisted_dependencies: List[str] = []
    max_retries: int = 3
    middlewares: List[Middleware] = []
    callback: Optional[BaseCallback] = None
    llm: Union[LLM, LangchainLLM] = None

    class Config:
        arbitrary_types_allowed = True


def load_config(override_config: Config = None):
    config = {}

    if override_config is None:
        override_config = {}

    try:
        with open("pandasai.json", "r") as f:
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

    config = Config(**config)

    return config
