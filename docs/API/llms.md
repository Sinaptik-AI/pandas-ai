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

### OpenAssistant

OpenAssistant wrapper extended through Base HuggingFace Class
     
::: pandasai.llm.open_assistant
    options:
      show_root_heading: true

### Starcoder

Starcoder wrapper extended through Base HuggingFace Class
      
::: pandasai.llm.starcoder
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