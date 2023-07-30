import pytest
import openai
from openai.openai_object import OpenAIObject

from pandasai import PandasAI
from pandasai.helpers import (
    OpenAICallbackHandler,
    get_openai_callback,
)
import pandas as pd

from pandasai.llm.openai import OpenAI


@pytest.fixture
def handler() -> OpenAICallbackHandler:
    return OpenAICallbackHandler()


class TestOpenAIInfo:
    """Unit tests for OpenAI Info Callback"""

    def test_handler(self, handler: OpenAICallbackHandler) -> None:
        response = OpenAIObject.construct_from(
            {
                "usage": {
                    "prompt_tokens": 2,
                    "completion_tokens": 1,
                    "total_tokens": 3,
                },
                "model": "gpt-35-turbo",
            }
        )

        handler(response)
        assert handler.total_tokens == 3
        assert handler.prompt_tokens == 2
        assert handler.completion_tokens == 1
        assert handler.total_cost > 0

    def test_handler_unknown_model(self, handler: OpenAICallbackHandler) -> None:
        response = OpenAIObject.construct_from(
            {
                "usage": {
                    "prompt_tokens": 2,
                    "completion_tokens": 1,
                    "total_tokens": 3,
                },
                "model": "foo-bar",
            }
        )

        handler(response)
        assert handler.total_tokens == 3
        assert handler.prompt_tokens == 2
        assert handler.completion_tokens == 1
        # cost must be 0.0 for unknown model
        assert handler.total_cost == 0.0

    def test_openai_callback(self, mocker):
        df = pd.DataFrame([1, 2, 3])
        llm = OpenAI(api_token="test")
        llm_response = OpenAIObject.construct_from(
            {
                "choices": [
                    {
                        "text": "```df.sum()```",
                        "index": 0,
                        "logprobs": None,
                        "finish_reason": "stop",
                        "start_text": "",
                    }
                ],
                "model": llm.model,
                "usage": {
                    "prompt_tokens": 2,
                    "completion_tokens": 1,
                    "total_tokens": 3,
                },
            }
        )
        mocker.patch.object(openai.ChatCompletion, "create", return_value=llm_response)

        pandas_ai = PandasAI(llm, enable_cache=False)
        with get_openai_callback() as cb:
            _ = pandas_ai(df, "some question")
            assert cb.total_tokens == 3
            assert cb.prompt_tokens == 2
            assert cb.completion_tokens == 1
            assert cb.total_cost > 0

        total_tokens = cb.total_tokens

        with get_openai_callback() as cb:
            pandas_ai(df, "some question")
            pandas_ai(df, "some question")

        assert cb.total_tokens == total_tokens * 2

        with get_openai_callback() as cb:
            pandas_ai(df, "some question")
            pandas_ai(df, "some question")
            pandas_ai(df, "some question")

        assert cb.total_tokens == total_tokens * 3
