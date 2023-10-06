# Custom instructions

In some cases, you may want to customize the instructions that are used by PandasAI. For example, you may want to use a different instruction for a specific use case to improve the results for certain types of queries.

With PandasAI, you can easily customize the instructions that are used by the library. You can do this by passing a `custom_instructions` string in the config dictionary to the `SmartDataframe` constructor.

## Example

```python
from pandasai import SmartDataframe

df = SmartDataframe("data.csv", {
    "custom_instructions": "Custom instructions for the generation of Python code"
})
```
