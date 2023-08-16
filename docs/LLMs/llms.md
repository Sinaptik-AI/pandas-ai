# Large language models (LLMs)

PandasAI supports several large language models (LLMs). LLMs are used to generate code from natural language queries. The generated code is then executed to produce the result.

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

llm = OpenAI(api_key="my-openai-api-key")
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

## HuggingFace models

In order to use HuggingFace models, you need to have a HuggingFace API key. You can create a HuggingFace account [here](https://huggingface.co/join) and get an API key [here](https://hf.co/settings/tokens).

Once you have an API key, you can use it to instantiate one of the HuggingFace models.

At the moment, PandasAI supports the following HuggingFace models:

- Starcoder: `bigcode/starcoder`
- Falcon: `tiiuae/falcon-7b-instruct`

```python
from pandasai import SmartDataframe
from pandasai.llm import Starcoder, Falcon

llm = Starcoder(api_key="my-huggingface-api-key")
# or
llm = Falcon(api_key="my-huggingface-api-key")

df = SmartDataframe("data.csv", config={"llm": llm})
```

As an alternative, you can set the `HUGGINGFACE_API_KEY` environment variable and instantiate the HuggingFace object without passing the API key:

```python
from pandasai import SmartDataframe
from pandasai.llm import Starcoder, Falcon

llm = Starcoder() # no need to pass the API key, it will be read from the environment variable
# or
llm = Falcon() # no need to pass the API key, it will be read from the environment variable

df = SmartDataframe("data.csv", config={"llm": llm})
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
from pandasai.llm import GoogleVertexai

llm = GoogleVertexai(project_id="generative-ai-training",
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
    api_key="my-azure-openai-api-key",
    api_base="my-azure-openai-api-endpoint",
    api_version="2023-05-15",
    deployment_name="my-deployment-name"
)
df = SmartDataframe("data.csv", config={"llm": llm})
```

As an alternative, you can set the `OPENAI_API_KEY`, `OPENAI_API_VERSION`, and `OPENAI_API_BASE` environment variables and instantiate the Azure OpenAI object without passing them:

```python
from pandasai import SmartDataframe
from pandasai.llm import AzureOpenAI

llm = AzureOpenAI(
    deployment_name="my-deployment-name"
) # no need to pass the API key, endpoint and API version. They are read from the environment variable
df = SmartDataframe("data.csv", config={"llm": llm})
```

If you are behind an explicit proxy, you can specify `openai_proxy` when instantiating the `AzureOpenAI` object or set the `OPENAI_PROXY` environment variable to pass through.
