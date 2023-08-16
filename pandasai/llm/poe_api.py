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
    Base LLM class is extended to support POEAPILLM.Below example shows how
    we can use override certain configurations to change model's behaviour.
    Example:
        >>> import pandas as pd
        >>> from pandasai import PandasAI
        >>> from pandasai.llm.POEAPI import POEAPI
        >>> model = POEAPI(bot_name='', token='')
        >>> df_ai = PandasAI(model)
        >>> response = df_ai(df, prompt='What is the sum of the GDP in this table?')
    
    
    """

    

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
            bot_name: The name of the model.
            token: The token of the Poe API.
            
        """
    
        try:
            import poe

            self.poe_api_bot = poe.Client(token=self.token
                
               
            )
        except ImportError:
            raise ImportError(
                "Unable to import poe-api python package "
                "Please install it with `pip install -U poe-api`"
            )


    

    @property
    def type(self) -> str:
        return "POEAPI"

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        prompt = str(instruction)
        prompt = prompt + value + suffix
        for chunk in self.poe_api_bot.send_message(self.bot_name ,prompt,):
            pass
        return chunk['text']