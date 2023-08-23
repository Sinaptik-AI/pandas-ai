"""Unit tests for the LLaMa2TextGen LLM class"""
from pandasai import Prompt
from pandasai.llm import LLaMa2TextGen


class MockPrompt(Prompt):
    text: str = "instruction."


class MockResponse:
    generated_text: str = ""

    def __init__(self, generated_text):
        self.generated_text = generated_text


class TestLLaMa2TextGen:
    """Unit tests for the LLaMa2TextGen LLM class"""

    def test_type_with_token(self):
        assert (
            LLaMa2TextGen(
                inference_server_url="http://127.0.0.1:8080"
            ).type == "llama2-text-generation"
        )

    def test_params_setting(self):
        llm = LLaMa2TextGen(
            inference_server_url="http://127.0.0.1:8080",
            max_new_tokens=1024,
            top_p=0.8,
            typical_p=0.8,
            temperature=1E-3,
            stop_sequences=["\n"],
            seed=0,
            do_sample=False,
            streaming=True,
            timeout=120,
            use_chat_model=False,
        )

        assert llm.client.base_url == "http://127.0.0.1:8080"
        assert llm.max_new_tokens == 1024
        assert llm.top_p == 0.8
        assert llm.temperature == 0.001
        assert llm.stop_sequences == ["\n"]
        assert llm.seed == 0
        assert not llm.do_sample
        assert llm.streaming
        assert llm.timeout == 120
        assert not llm.use_chat_model

    def test_completion(self, mocker):
        tgi_mock = mocker.patch("text_generation.Client.generate")
        expected_text = "This is the generated text."
        tgi_mock.return_value = MockResponse(expected_text)

        llm = LLaMa2TextGen(
            inference_server_url="http://127.0.0.1:8080"
        )

        instruction = MockPrompt()
        result = llm.call(instruction)

        tgi_mock.assert_called_once_with(
            instruction.to_string(),
            max_new_tokens=llm.max_new_tokens,
            top_k=llm.top_k,
            top_p=llm.top_p,
            typical_p=llm.typical_p,
            temperature=llm.temperature,
            repetition_penalty=llm.repetition_penalty,
            truncate=llm.truncate,
            stop_sequences=llm.stop_sequences,
            do_sample=llm.do_sample,
            seed=llm.seed,
        )

        assert result == expected_text

    def test_chat_completion(self, mocker):
        tgi_mock = mocker.patch("text_generation.Client.generate")
        expected_text = "This is the generated text."
        tgi_mock.return_value = MockResponse(expected_text)

        llm = LLaMa2TextGen(
            inference_server_url="http://127.0.0.1:8080",
            use_chat_model=True,
        )

        instruction = MockPrompt()
        result = llm.call(instruction)

        chat_prompt = f"[INST] <<SYS>>\n{instruction.to_string()}\n<</SYS>>\n\n"
        tgi_mock.assert_called_once_with(
            chat_prompt,
            max_new_tokens=llm.max_new_tokens,
            top_k=llm.top_k,
            top_p=llm.top_p,
            typical_p=llm.typical_p,
            temperature=llm.temperature,
            repetition_penalty=llm.repetition_penalty,
            truncate=llm.truncate,
            stop_sequences=llm.stop_sequences,
            do_sample=llm.do_sample,
            seed=llm.seed,
        )

        assert result == expected_text
