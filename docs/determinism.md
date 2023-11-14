# Determinism
## Introduction
In the realm of Language Model (LM) applications, determinism plays a crucial role, especially when consistent and predictable outcomes are desired. Our library, which integrates multiple LLMs including OpenAI's models, offers users the ability to control this aspect of model behavior through specific parameters like temperature and seed. This document aims to elucidate the importance of these parameters, their usage, and current limitations with different LLM instances such as AzureOpenAI.

## Why Determinism Matters
Determinism in language models refers to the ability to produce the same output consistently given the same input under identical conditions. This characteristic is vital for:

- Reproducibility: Ensuring the same results can be obtained across different runs, which is crucial for debugging and iterative development.
- Consistency: Maintaining uniformity in responses, particularly important in scenarios like automated customer support, where varied responses to the same query might be undesirable.
- Testing: Facilitating the evaluation and comparison of models or algorithms by providing a stable ground for testing.

## The Role of temperature=0
The temperature parameter in language models controls the randomness of the output. A higher temperature increases diversity and creativity in responses, while a lower temperature makes the model more predictable and conservative. Setting `temperature=0` essentially turns off randomness, leading the model to choose the most likely next word at each step. This is critical for achieving determinism as it minimizes variance in the model's output.

## Implications of temperature=0
- Predictable Responses: The model will consistently choose the most probable path, leading to high predictability in outputs.
- Creativity: The trade-off for predictability is reduced creativity and variation in responses, as the model won't explore less likely options.

## Utilizing seed for Enhanced Control
The seed parameter is another tool to enhance determinism. It sets the initial state for the random number generator used in the model, ensuring that the same sequence of "random" numbers is used for each run. This parameter, when combined with `temperature=0`, offers an even higher degree of predictability.

## Example:
```py
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

# Sample DataFrame
df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

# Instantiate a LLM
llm = OpenAI(
    api_token="YOUR_API_TOKEN",
    temperature=0,
    seed=26
)

df = SmartDataframe(df, config={"llm": llm})
df.chat('Which are the 5 happiest countries?') # answer should me (mostly) consistent across devices.
```

## Current Limitation:
### AzureOpenAI Instance
While the seed parameter is effective with the OpenAI instance in our library, it's important to note that this functionality is not yet available for AzureOpenAI. Users working with AzureOpenAI can still use `temperature=0` to reduce randomness but without the added predictability that seed offers.

### System fingerprint
As mentioned in the documentation ([OpenAI Seed](https://platform.openai.com/docs/guides/text-generation/reproducible-outputs)) :
> Sometimes, determinism may be impacted due to necessary changes OpenAI makes to model configurations on our end. To help you keep track of these changes, we expose the system_fingerprint field. If this value is different, you may see different outputs due to changes we've made on our systems.

## Workarounds and Future Updates
For AzureOpenAI Users: Rely on `temperature=0` for reducing randomness. Stay tuned for future updates as we work towards integrating seed functionality with AzureOpenAI.
For OpenAI Users: Utilize both `temperature=0` and seed for maximum determinism.


