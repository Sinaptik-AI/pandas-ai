"""GPT4All LLMs
This module provides a family of commercially / non-commercially available 
LLMs maintained by Nomic AI. With GPT4All we can easily download models like 
Falcon, Llama etc and run them seamlessly using CPU with lower RAMs. 

Example:
    Use below example to call GPT4All supporrted models

    >>> from pandasai.llm.gpt4all import GPT4AllLLM
"""
import logging
import os
import sys
import time
from typing import Optional

import requests
from tqdm import tqdm
try:
    from gpt4all import GPT4All
except ImportError:
    raise ImportError(
        "Unable to import gpt4all python package "
        "Please install it with `pip install -U gpt4all`"
    )

from pandasai.prompts.base import Prompt
from .base import LLM

logger = logging.getLogger(__name__)


class UnableToDownloadGPT4AllBin(Exception):
    """
    Raised when unable to automatically download the GPT4All LLM.

    Args:
        Exception (Exception): UnableToDownloadGPT4AllBin
    """

    def __init__(self, gpt4all_bin_filename=None, time_spent=None):
        """
        Initialize `UnableToDownloadGPT4AllBin` instance.

        Args:
            gpt4all_bin_filename (Optional[str]): Name of the binary file of
                the GPT4All model.
            time_spent (Optional[int]): Time in seconds spent for
                downloading process.
        """

        self.gpt4all_bin_filename = gpt4all_bin_filename
        self.time_s_spent = time_spent

        super().__init__(
            f"Unable to download the model. "
            f"Model filename: {gpt4all_bin_filename or 'Unknown'}; "
            f"Time spent: {time_spent or 'Unknown'}"
        )


class GPT4AllLLM(LLM):
    """GPT4All LLMs API
    Base LLM class is extended to support GPT4All LLM. When this class will be
    initialized all the additional parameters like temp, top_p, top_k etc should
    be inside **kwargs while instantiating the class. That is to be done only if
    the user wants to override the existing configurations. Below example shows how
    we can use override certain configurations to change model's behaviour.

    Example:
        >>> import pandas as pd
        >>> from pandasai import PandasAI
        >>> from pandasai.llm.gpt4all import GPT4AllLLM

        >>> model_name = 'ggml-replit-code-v1-3b.bin'
        >>> additional_params = {'temp': 0, 'max_tokens': 50}
        >>> model = GPT4AllLLM(model_name, allow_download=True, **additional_params)

        >>> df_ai = PandasAI(model)
        >>> response = df_ai(df, prompt='What is the sum of the GDP in this table?')

    There is an optional parameter called model_path which sets where to
    download the model and if it is not set then it will download the model
    inside the folder: home/<user-name>/.local/share/nomic.ai/GPT4All/
    Note: Please note that right now Pandas AI only supports models for gpt4all. However
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

    _model_repo_url = "https://gpt4all.io/models/models.json"
    _default_download_path_unix = os.path.join(
        os.path.expanduser("~"), ".local/share/nomic.ai/GPT4All/"
    )
    _default_download_path_win = os.path.join(os.path.expanduser("~"), ".gpt4all\\")
    _supported_models = [
        metadata["filename"] for metadata in requests.get(_model_repo_url).json()
    ]

    def __init__(
        self,
        model_name: str,
        model_folder_path: Optional[str] = None,
        allow_download: Optional[bool] = False,
        n_threads: Optional[int] = 4,
        download_chunk_size: Optional[int] = 8912,
        **kwargs,
    ) -> None:
        """
        GPT4All client for using Pandas AI
        Args:
            model_name: The name of the model.
            model_folder_path: The folder inside the model weights are present
            allow_download: If True will trigger download the specified model
            n_threads: Number of CPU threads to be used while running the model
            download_chunk_size: The chunk size set for downloading the model
        """
        self.model_name = (
            f"{model_name}.bin" if not model_name.endswith(".bin") else model_name
        )
        self.chunk_size = download_chunk_size

        _assert_msg = (
            "Model not Found. Please check the list of supported models:",
            self._supported_models,
        )
        assert self.model_name in self._supported_models, _assert_msg

        default_download_path = self._default_download_path_unix
        if sys.platform.startswith("win"):
            default_download_path = self._default_download_path_win

        self.model_folder_path = (
            default_download_path if model_folder_path is None else model_folder_path
        )

        # automatically create the default folder and download the model

        if not os.path.exists(self.model_folder_path) and allow_download:
            os.mkdir(self.model_folder_path)

        self.allow_download = allow_download
        if allow_download:
            self._auto_download()
            logger.info(f"Model {model_name} saved as: {self.model_folder_path}")

        n_threads = self.n_threads if n_threads is None else n_threads
        self.gpt4all_model = GPT4All(
            model_name=self.model_name,
            model_path=self.model_folder_path,
            n_threads=n_threads,
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

    def _auto_download(self) -> None:
        """
        Automatically download GPT4All binary file.

        Download from gpt4all.io using the following URL:
        `https://gpt4all.io/models/<self.model_name>`
        where `model_name` is the name of binary file of the model.

        The downloading starts if `self.allow_download` is `True` and
        a binary file (supposed to contain content of the model)
        was not found in `download_path`.

        Raises:
        """
        download_path = os.path.join(self.model_folder_path, self.model_name)

        if not os.path.exists(download_path):
            if self.allow_download:
                # send a GET request to the URL to download the file.
                # Stream it while downloading, since the file is large
                url = f"https://gpt4all.io/models/{self.model_name}"

                start_downloading_ts = time.time()
                try:
                    response = requests.get(url, stream=True)

                    with open(download_path, "wb") as f:
                        for chunk in tqdm(
                            response.iter_content(chunk_size=self.chunk_size)
                        ):
                            if chunk:
                                f.write(chunk)

                except Exception as exc:
                    logger.error("=> Download Failed.", exc_info=True)
                    raise UnableToDownloadGPT4AllBin(
                        gpt4all_bin_filename=self.model_name,
                        time_spent=(int(time.time()) - start_downloading_ts),
                    ) from exc

                logger.info(
                    f"The model was successfully downloaded in "
                    f"{(int(time.time()) - start_downloading_ts)} seconds."
                )

                print(f"=> Model: {self.model_name} downloaded successfully 🥳")

            else:
                print(
                    f"{self.model_name} does not exists in {self.model_folder_path}",
                    "Please either download the model by allow_download = True",
                )

    @property
    def type(self) -> str:
        return "gpt4all"

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        prompt = str(instruction)
        prompt = prompt + value + suffix
        return self.gpt4all_model.generate(prompt, **self.params)
