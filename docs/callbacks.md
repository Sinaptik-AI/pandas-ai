# Callbacks

Callbacks are functions that are called at specific points during the execution of the `PandasAI` class. They can be used, for example, to get the code as soon as it is generated.

```python
from pandasai import SmartDataframe
from pandasai.callbacks import StdoutCallback

# The callback will print the generated code to the console as soon as it is generated
df = SmartDataframe("data.csv", {"callback": StdoutCallback()})
```

## Creating a custom callback

To create a custom callback, you must inherit from the `BaseCallback` class and implement the methods you want to use.

```python
from pandasai import SmartDataframe
from pandasai.callbacks import BaseCallback

# MyCallback
class MyCustomCallback(BaseCallback):
    def on_code(self, response: str):
        # Do something with the generated code
        ...

df = SmartDataframe("data.csv", {"callback": MyCustomCallback()})
```

## Built-in callbacks

PandasAI comes with a few built-in callbacks that can be used to modify the generated code.

### `StdoutCallback`

The `StdoutCallback` callback prints the generated code to the console as soon as it is generated.

```python
from pandasai import SmartDataframe
from pandasai.callbacks import BaseCallback, StdoutCallback

# The callback will print the generated code to the console as soon as it is generated
df = SmartDataframe("data.csv", {"callback": StdoutCallback()})
```

### `FileCallback`

The `FileCallback` callback writes the generated code to a file as soon as it is generated.

```python
from pandasai import SmartDataframe
from pandasai.callbacks import FileCallback

# The callback will write the generated code to a file as soon as it is generated
df = SmartDataframe("data.csv", {"callback": FileCallback("output.py")})
```
