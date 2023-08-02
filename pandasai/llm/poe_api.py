"""Poe-Api LLMs

This module provides a family of commercially / non-commercially available 
LLMs maintained by Quora 
Example:
    Use below example to call POEAPI supporrted models
    >>> from pandasai.llm.poe_api import POEAPI
"""
import os
import requests
from typing import Optional

from pandasai.prompts.base import Prompt
from .base import LLM


class POEAPI(LLM):
    """POEAPI LLMs API
    Base LLM class is extended to support POEAPILLM. When this class will be
    initialized all the additional parameters like temp, top_p, top_k etc should
    be inside **kwargs while instantiating the class. That is to be done only if
    the user wants to override the existing configurations. Below example shows how
    we can use override certain configurations to change model's behaviour.
    Example:
        >>> import pandas as pd
        >>> from pandasai import PandasAI
        >>> from pandasai.llm.POEAPI import POEAPILLM
        >>> model_name = 'ggml-replit-code-v1-3b.bin'
        >>> additional_params = {'temp': 0, 'max_tokens': 50}
        >>> model = POEAPILLM(model_name, allow_download=True, **additional_params)
        >>> df_ai = PandasAI(model)
        >>> response = df_ai(df, prompt='What is the sum of the GDP in this table?')
    There is an optional parameter called model_path which sets where to
    download the model and if it is not set then it will download the model
    inside the folder: home/<user-name>/.local/share/nomic.ai/POEAPI/
    Note: Please note that right now Pandas AI only supports models for POEAPI. However
    it might not work as chatGPT when it comes to performance, hence for now users using
    this module have to tune the existing prompts to get better results.
    """

    temp: Optional[float] = 0
    top_p: Optional[float] = 0.1
    top_k: Optional[int] = 40
    n_batch: Optional[int] = 8
    n_threads: Optional[int] = 4
    n_predict: Optional[int] = 256
    max_tokens: Optional[int] = 200
    repeat_last_n: Optional[int] = 64
    repeat_penalty: Optional[float] = 1.18

    _model_repo_url = "https://POEAPI.io/models/models.json"
    _supported_models = [
        metadata["filename"] for metadata in requests.get(_model_repo_url).json()
    ]

    def __init__(
        self,
        bot_name: str,
        token : str,
        **kwargs,
    ) -> None:
        self.bot_name = bot_name
        self.token = token
        """
        POEAPI client for using Pandas AI
        Args:
            model_name: The name of the model.
            model_folder_path: The folder inside the model weights are present
            allow_download: If True will trigger download the specified model
            n_threads: Number of CPU threads to be used while running the model
            download_chunk_size: The chunk size set for downloading the model
        """
        

        # automatically create the default folder and download the model

        try:
            from poe import Client

            self.poe_api = Client(token=self.token
                
               
            )
        except ImportError:
            raise ImportError(
                "Unable to import poe-api python package "
                "Please install it with `pip install -U poe-api`"
            )

        self.default_parameters = {
            "max_tokens": self.max_tokens,
            "n_predict": self.n_predict,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temp": self.temp,
            "n_batch": self.n_batch,
            "repeat_penalty": self.repeat_penalty,
            "repeat_last_n": self.repeat_last_n,
        }

        # this will override all the parameters with all the pre-existing ones
        self.params = {**self.default_parameters, **kwargs}

    

    @property
    def type(self) -> str:
        return "POEAPI"

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        prompt = str(instruction)
        prompt = prompt + value + suffix
        for chunk in self.poe_api.send_message(self.bot_name ,prompt,):
            pass
        return chunk['text']