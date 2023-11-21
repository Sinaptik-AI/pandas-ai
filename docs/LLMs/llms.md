# Large language models (LLMs)

PandasAI supports several large language models (LLMs). LLMs are used to generate code from natural language queries. The generated code is then executed to produce the result.

[![Choose the LLM](https://cdn.loom.com/sessions/thumbnails/5496c9c07ee04f69bfef1bc2359cd591-00001.jpg)](https://www.loom.com/share/5496c9c07ee04f69bfef1bc2359cd591 "Choose the LLM")

You can either choose a LLM by instantiating one and passing it to the `SmartDataFrame` or `SmartDatalake` constructor, or you can specify one in the `pandasai.json` file.

If the model expects one or more parameters, you can pass them to the constructor or specify them in the `pandasai.json` file, in the `llm_options` param, as it follows:

```json
{
  "llm": "OpenAI",
  "llm_options": {
    "api_token": "API_TOKEN_GOES_HERE"
  }
}
```

## OpenAI models

In order to use OpenAI models, you need to have an OpenAI API key. You can get one [here](https://platform.openai.com/account/api-keys).

Once you have an API key, you can use it to instantiate an OpenAI object:

```python
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

llm = OpenAI(api_token="my-openai-api-key")
pandas_ai = SmartDataframe("data.csv", config={"llm": llm})
```

As an alternative, you can set the `OPENAI_API_KEY` environment variable and instantiate the `OpenAI` object without passing the API key:

```python
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

llm = OpenAI() # no need to pass the API key, it will be read from the environment variable
pandas_ai = SmartDataframe("data.csv", config={"llm": llm})
```

If you are behind an explicit proxy, you can specify `openai_proxy` when instantiating the `OpenAI` object or set the `OPENAI_PROXY` environment variable to pass through.

### Count tokens

You can count the number of tokens used by a prompt as follows:

```python
"""Example of using PandasAI with a pandas dataframe"""

from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.helpers.openai_info import get_openai_callback
import pandas as pd

llm = OpenAI()

# conversational=False is supposed to display lower usage and cost
df = SmartDataframe("data.csv", {"llm": llm, "conversational": False})

with get_openai_callback() as cb:
    response = df.chat("Calculate the sum of the gdp of north american countries")

    print(response)
    print(cb)
#  The sum of the GDP of North American countries is 19,294,482,071,552.
#  Tokens Used: 375
#	Prompt Tokens: 210
#	Completion Tokens: 165
# Total Cost (USD): $ 0.000750
```

## Google PaLM

In order to use Google PaLM models, you need to have a Google Cloud API key. You can get one [here](https://developers.generativeai.google/tutorials/setup).

Once you have an API key, you can use it to instantiate a Google PaLM object:

```python
from pandasai import SmartDataframe
from pandasai.llm import GooglePalm

llm = GooglePalm(api_key="my-google-cloud-api-key")
df = SmartDataframe("data.csv", config={"llm": llm})
```

## Google Vertexai

In order to use Google PaLM models through Vertexai api, you need to have

1. Google Cloud Project
2. Region of Project Set up
3. Install optional dependency `google-cloud-aiplatform `
4. Authentication of `gcloud`

Once you have basic setup, you can use it to instantiate a Google PaLM through vertex ai:

```python
from pandasai import SmartDataframe
from pandasai.llm import GoogleVertexAI

llm = GoogleVertexAI(project_id="generative-ai-training",
                     location="us-central1",
                     model="text-bison@001")
df = SmartDataframe("data.csv", config={"llm": llm})
```

## Azure OpenAI

In order to use Azure OpenAI models, you need to have an Azure OpenAI API key as well as an Azure OpenAI endpoint. You can get one [here](https://azure.microsoft.com/products/cognitive-services/openai-service).

To instantiate an Azure OpenAI object you also need to specify the name of your deployed model on Azure and the API version:

```python
from pandasai import SmartDataframe
from pandasai.llm import AzureOpenAI

llm = AzureOpenAI(
    api_token="my-azure-openai-api-key",
    azure_endpoint="my-azure-openai-api-endpoint",
    api_version="2023-05-15",
    deployment_name="my-deployment-name"
)
df = SmartDataframe("data.csv", config={"llm": llm})
```

As an alternative, you can set the `AZURE_OPENAI_API_KEY`, `OPENAI_API_VERSION`, and `AZURE_OPENAI_ENDPOINT` environment variables and instantiate the Azure OpenAI object without passing them:

```python
from pandasai import SmartDataframe
from pandasai.llm import AzureOpenAI

llm = AzureOpenAI(
    deployment_name="my-deployment-name"
) # no need to pass the API key, endpoint and API version. They are read from the environment variable
df = SmartDataframe("data.csv", config={"llm": llm})
```

If you are behind an explicit proxy, you can specify `openai_proxy` when instantiating the `AzureOpenAI` object or set the `OPENAI_PROXY` environment variable to pass through.

## HuggingFace via Text Generation

In order to use HuggingFace models via text-generation, you need to first serve a supported large language model (LLM). Read [text-generation docs](https://huggingface.co/docs/text-generation-inference/index) for more on how to setup an inference server.

This can be used, for example, to use models like LLaMa2, CodeLLaMa, etc. You can find more information about text-generation [here](https://huggingface.co/docs/text-generation-inference/index).

The `inference_server_url` is the only required parameter to instantiate an `HuggingFaceTextGen` model:

```python
from pandasai.llm import HuggingFaceTextGen
from pandasai import SmartDataframe

llm = HuggingFaceTextGen(
    inference_server_url="http://127.0.0.1:8080"
)
df = SmartDataframe("data.csv", config={"llm": llm})
```

## LangChain models

PandasAI has also built-in support for [LangChain](https://langchain.com/) models.

In order to use LangChain models, you need to install the `langchain` package:

```bash
pip install pandasai[langchain]
```

Once you have installed the `langchain` package, you can use it to instantiate a LangChain object:

```python
from pandasai import SmartDataframe
from langchain.llms import OpenAI

langchain_llm = OpenAI(openai_api_key="my-openai-api-key")
df = SmartDataframe("data.csv", {"llm": langchain_llm})
```

PandasAI will automatically detect that you are using a LangChain LLM and will convert it to a PandasAI LLM.

### More information

For more information about LangChain models, please refer to the [LangChain documentation](https://python.langchain.com/en/latest/reference/modules/llms.html).
