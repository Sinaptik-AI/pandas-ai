import os
from dotenv import load_dotenv
from .base import LLM
import openai

load_dotenv()

class OpenAI(LLM):
  api_token: str
  model: str = "gpt-3.5-turbo"
  temperature: float = 0
  max_tokens: int = 512
  top_p: float = 1
  frequency_penalty: float = 0
  presence_penalty: float = 0.6
  stop: str = None

  def __init__(self, api_token: str = None, model: str = None, temperature: float = None, max_tokens: int = None, top_p: float = None, frequency_penalty: float = None, presence_penalty: float = None, stop: str = None):
    self.api_token = api_token or os.getenv("OPENAI_API_KEY")
    if (self.api_token is None):
      raise Exception("OpenAI API key is required")
    openai.api_key = self.api_token
    
    self.model = model or self.model
    self.temperature = temperature or self.temperature
    self.max_tokens = max_tokens or self.max_tokens
    self.top_p = top_p or self.top_p
    self.frequency_penalty = frequency_penalty or self.frequency_penalty
    self.presence_penalty = presence_penalty or self.presence_penalty
    self.stop = stop or self.stop
  
  def completion(self, prompt: str) -> str:
    params = {
      "model": self.model,
      "prompt": prompt,
      "temperature": self.temperature,
      "max_tokens": self.max_tokens,
      "top_p": self.top_p,
      "frequency_penalty": self.frequency_penalty,
      "presence_penalty": self.presence_penalty
    }

    if self.stop is not None:
        params["stop"] = [self.stop]

    response = openai.Completion.create(**params)

    return response["choices"][0]["text"]
  
  def chat_completion(self, prompt: str) -> str:
    params = {
      "model": self.model,
      "temperature": self.temperature,
      "max_tokens": self.max_tokens,
      "top_p": self.top_p,
      "frequency_penalty": self.frequency_penalty,
      "presence_penalty": self.presence_penalty,
      "messages": [{
        "role": "system",
        "content": prompt,
      }]
    }

    if self.stop is not None:
        params["stop"] = [self.stop]

    response = openai.ChatCompletion.create(**params)

    return response["choices"][0]["message"]["content"]

  def call(self, instruction: str, input: str) -> str:
    if (self.model == "text-davinci-003"):
      response = self.completion(str(instruction) + str(input))
    elif (self.model == "gpt-3.5-turbo"):
      response = self.chat_completion(str(instruction) + str(input))
    else:
      raise Exception("Unsupported model")

    return response

  @property
  def _type(self) -> str:
      return "openai"