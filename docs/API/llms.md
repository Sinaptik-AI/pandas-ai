## LLMs

This document outlines the LLMs API wrappers included in the `pandasai`.

### Base

This is a base class to implement any LLM to be used with `pandasai` framework.

::: pandasai.llm.base
options:
show_root_heading: true

### OpenAI

OpenAI API wrapper extended through BaseOpenAI class.

::: pandasai.llm.openai
options:
show_root_heading: true

### Starcoder (deprecated)

Starcoder wrapper extended through Base HuggingFace Class

- Note: Starcoder is deprecated and will be removed in future versions. Please use another LLM.

::: pandasai.llm.starcoder
options:
show_root_heading: true

### Falcon (deprecated)

Falcon wrapper extended through Base HuggingFace Class

- Note: Falcon is deprecated and will be removed in future versions. Please use another LLM.

::: pandasai.llm.falcon
options:
show_root_heading: true

### Azure OpenAI

OpenAI API through Azure Platform wrapper

::: pandasai.llm.azure_openai
options:
show_root_heading: true

### GooglePalm

GooglePalm class extended through BaseGoogle Class

::: pandasai.llm.google_palm
options:
show_root_heading: true

### Fake

A test fake class
::: pandasai.llm.fake
options:
show_root_heading: true
