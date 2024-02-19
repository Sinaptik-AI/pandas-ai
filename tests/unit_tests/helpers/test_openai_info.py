import pandas as pd
import pytest
from pandasai.agent import Agent
from pandasai.helpers import (
    OpenAICallbackHandler,
    get_openai_callback,
)
from pandasai.llm.openai import OpenAI


class OpenAIObject:
    def __init__(self, dictionary):
        self.__dict__.update(dictionary)


@pytest.fixture
def handler() -> OpenAICallbackHandler:
    return OpenAICallbackHandler()


class TestOpenAIInfo:
    """Unit tests for OpenAI Info Callback"""

    def test_handler(self, handler: OpenAICallbackHandler) -> None:
        response = OpenAIObject(
            {
                "usage": OpenAIObject(
                    {
                        "prompt_tokens": 2,
                        "completion_tokens": 1,
                        "total_tokens": 3,
                    }
                ),
                "model": "gpt-35-turbo",
            }
        )

        handler(response)
        assert handler.total_tokens == 3
        assert handler.prompt_tokens == 2
        assert handler.completion_tokens == 1
        assert handler.total_cost > 0

    def test_handler_unknown_model(self, handler: OpenAICallbackHandler) -> None:
        response = OpenAIObject(
            {
                "usage": OpenAIObject(
                    {
                        "prompt_tokens": 2,
                        "completion_tokens": 1,
                        "total_tokens": 3,
                    }
                ),
                "model": "foo-bar",
            }
        )

        handler(response)
        assert handler.total_tokens == 3
        assert handler.prompt_tokens == 2
        assert handler.completion_tokens == 1
        # cost must be 0.0 for unknown model
        assert handler.total_cost == 0.0

    @pytest.mark.parametrize(
        "model_name,expected_cost",
        [
            ("gpt-3.5-turbo", 0.002),
            (
                "gpt-3.5-turbo-0613",
                0.002,
            ),
            (
                "gpt-3.5-turbo-16k-0613",
                0.002,
            ),
            (
                "gpt-3.5-turbo-1106",
                0.002,
            ),
            (
                "gpt-3.5-turbo-16k",
                0.002,
            ),
            ("gpt-4", 0.09),
            ("gpt-4-0613", 0.09),
            ("gpt-4-32k", 0.18),
            ("gpt-4-32k-0613", 0.18),
            ("gpt-4-1106-preview", 0.04),
        ],
    )
    def test_handler_openai(
        self, handler: OpenAICallbackHandler, model_name: str, expected_cost: float
    ) -> None:
        response = OpenAIObject(
            {
                "usage": OpenAIObject(
                    {
                        "prompt_tokens": 1000,
                        "completion_tokens": 1000,
                        "total_tokens": 2000,
                    }
                ),
                "model": model_name,
            }
        )
        handler(response)
        assert handler.total_cost == expected_cost

    @pytest.mark.parametrize(
        "model_name,expected_cost",
        [
            ("gpt-35-turbo", 0.0035),
            (
                "gpt-35-turbo-0613",
                0.0035,
            ),
            (
                "gpt-35-turbo-16k-0613",
                0.007,
            ),
            (
                "gpt-35-turbo-16k",
                0.007,
            ),
            ("gpt-4", 0.09),
            ("gpt-4-0613", 0.09),
            ("gpt-4-32k", 0.18),
            ("gpt-4-32k-0613", 0.18),
        ],
    )
    def test_handler_azure_openai(
        self, handler: OpenAICallbackHandler, model_name: str, expected_cost: float
    ) -> None:
        response = OpenAIObject(
            {
                "usage": OpenAIObject(
                    {
                        "prompt_tokens": 1000,
                        "completion_tokens": 1000,
                        "total_tokens": 2000,
                    }
                ),
                "model": model_name,
            }
        )
        handler(response)
        assert handler.total_cost == expected_cost

    @pytest.mark.parametrize(
        "model_name, expected_cost",
        [
            ("ft:gpt-3.5-turbo-0613:your-org:custom-model-name:1abcdefg", 0.028),
            ("gpt-35-turbo-0613.ft-0123456789abcdefghijklmnopqrstuv", 0.0035),
        ],
    )
    def test_handler_finetuned_model(
        self, handler: OpenAICallbackHandler, model_name: str, expected_cost: float
    ):
        response = OpenAIObject(
            {
                "usage": OpenAIObject(
                    {
                        "prompt_tokens": 1000,
                        "completion_tokens": 1000,
                        "total_tokens": 2000,
                    }
                ),
                "model": model_name,
            }
        )
        handler(response)
        assert handler.total_cost == expected_cost

    def test_openai_callback(self, mocker):
        df = pd.DataFrame([1, 2, 3])
        llm = OpenAI(api_token="test")
        llm_response = OpenAIObject(
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
                "usage": OpenAIObject(
                    {
                        "prompt_tokens": 2,
                        "completion_tokens": 1,
                        "total_tokens": 3,
                    }
                ),
            }
        )
        mocker.patch.object(llm.client, "create", return_value=llm_response)

        # Mock the check_if_related_to_conversation method to not
        # perform additional api requests to OpenAI
        mocker.patch.object(
            Agent,
            "check_if_related_to_conversation",
            return_value=False,
        )

        agent = Agent([df], config={"llm": llm, "enable_cache": False})
        with get_openai_callback() as cb:
            agent.chat("some question 1")
            assert cb.total_tokens == 3
            assert cb.prompt_tokens == 2
            assert cb.completion_tokens == 1
            assert cb.total_cost > 0

        total_tokens = cb.total_tokens

        with get_openai_callback() as cb:
            agent.chat("some question 2")
            agent.chat("some question 3")

        assert cb.total_tokens == total_tokens * 2

        with get_openai_callback() as cb:
            agent.chat("some question 4")
            agent.chat("some question 5")
            agent.chat("some question 6")

        assert cb.total_tokens == total_tokens * 3
