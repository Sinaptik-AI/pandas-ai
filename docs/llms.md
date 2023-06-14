# Large language models (LLMs)

PandasAI supports several large language models (LLMs).

## OpenAI models

In order to use OpenAI models, you need to have an OpenAI API key. You can get one [here](https://platform.openai.com/).

Once you have an API key, you can use it to instantiate an OpenAI object:

```python
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

llm = OpenAI(openai_api_key="my-openai-api-key")
pandas_ai = PandasAI(llm=llm)
```

As an alternative, you can set the `OPENAI_API_KEY` environment variable and instantiate the OpenAI object without passing the API key:

```python
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

llm = OpenAI() # no need to pass the API key, it will be read from the environment variable
pandas_ai = PandasAI(llm=llm)
```

## HuggingFace models

In order to use HuggingFace models, you need to have a HuggingFace API key. You can get one [here](https://huggingface.co/join).

Once you have an API key, you can use it to instantiate one of the HuggingFace models.

At the moment, PandasAI supports the following HuggingFace models:

- Starcoder: `bigcode/starcoder`
- OpenAssistant: `OpenAssistant/oasst-sft-1-pythia-12b`
- Falcon: `tiiuae/falcon-7b-instruct`

```python
from pandasai import PandasAI
from pandasai.llm.starcoder import Starcoder
from pandasai.llm.open_assistant import OpenAssistant
from pandasai.llm.falcon import Falcon

llm = Starcoder(huggingface_api_key="my-huggingface-api-key")
# or
llm = OpenAssistant(huggingface_api_key="my-huggingface-api-key")
# or
llm = Falcon(huggingface_api_key="my-huggingface-api-key")

pandas_ai = PandasAI(llm=llm)
```

As an alternative, you can set the `HUGGINGFACE_API_KEY` environment variable and instantiate the HuggingFace object without passing the API key:

```python
from pandasai import PandasAI
from pandasai.llm.starcoder import Starcoder
from pandasai.llm.open_assistant import OpenAssistant
from pandasai.llm.falcon import Falcon

llm = Starcoder() # no need to pass the API key, it will be read from the environment variable
# or
llm = OpenAssistant() # no need to pass the API key, it will be read from the environment variable
# or
llm = Falcon() # no need to pass the API key, it will be read from the environment variable

pandas_ai = PandasAI(llm=llm)
```

## Google PaLM

In order to use Google PaLM models, you need to have a Google Cloud API key. You can get one [here](https://developers.generativeai.google/tutorials/setup).

Once you have an API key, you can use it to instantiate a Google PaLM object:

```python
from pandasai import PandasAI
from pandasai.llm.google_palm import GooglePalm

llm = GooglePalm(google_cloud_api_key="my-google-cloud-api-key")
pandas_ai = PandasAI(llm=llm)
```

## Azure OpenAI

In order to use Azure OpenAI models, you need to have an Azure API key. You can get one [here](https://azure.microsoft.com/it-it/products/cognitive-services/openai-service).

Once you have an API key, you can use it to instantiate an Azure OpenAI object:

```python
from pandasai import PandasAI
from pandasai.llm.azure_openai import AzureOpenAI

llm = AzureOpenAI(azure_openai_api_key="my-azure-openai-api-key")
pandas_ai = PandasAI(llm=llm)
```

As an alternative, you can set the `AZURE_OPENAI_KEY` environment variable and instantiate the Azure OpenAI object without passing the API key:

```python
from pandasai import PandasAI
from pandasai.llm.azure_openai import AzureOpenAI

llm = AzureOpenAI() # no need to pass the API key, it will be read from the environment variable
pandas_ai = PandasAI(llm=llm)
```
