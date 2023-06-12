# Custom optional dependencies

By default, `pandasai` only allows to run code that uses some whitelisted modules. This is to prevent malicious code from being executed on the server or locally. However, it is possible to add custom modules to the whitelist. This can be done by passing a list of modules to the `custom_whitelisted_dependencies` parameter when instantiating the `PandasAI` object:

```python
pandas_ai = PandasAI(llm, custom_whitelisted_dependencies=["my_custom_library"])
```

The `custom_whitelisted_dependencies` parameter accepts a list of strings, where each string is the name of a module. The module must be installed in the environment where `pandasai` is running.

Please, make sure you have installed the module in the environment where `pandasai` is running. Otherwise, you will get an error when trying to run the code.
