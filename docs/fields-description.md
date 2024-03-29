# Use custom field descriptions

The `field_descriptions` is a dictionary attribute of the `BaseConnector` class. It is used to provide additional information or descriptions about each individual field in the data source. This can be useful for providing context or explanations for the data in each field, especially when the field names themselves are not self-explanatory.

Here's an example of how you might use `field_descriptions`:

```python
field_descriptions = {
    'user_id': 'The unique identifier for each user',
    'payment_id': 'The unique identifier for each payment',
    'payment_provider': 'The payment provider used for the payment (e.g. PayPal, Stripe, etc.)'
}
```

In this example, `user_id`, `payment_id`, and `payment_provider` are the names of the fields in the data source, and the corresponding values are descriptions of what each field represents.

When initializing a `BaseConnector` instance (or any other connector), you can pass in this `field_descriptions` dictionary as an argument:

```python
connector = BaseConnector(config, name='My Connector', field_descriptions=field_descriptions)
```

Another example using a pandas connector:

```python
import pandas as pd
from pandasai.connectors import PandasConnector
from pandasai import SmartDataframe

df = pd.DataFrame({
    'user_id': [1, 2, 3],
    'payment_id': [101, 102, 103],
    'payment_provider': ['PayPal', 'Stripe', 'PayPal']
})
connector = PandasConnector({"original_df": df}, field_descriptions=field_descriptions)
sdf = SmartDataframe(connector)
sdf.chat("What is the most common payment provider?")
# Output: PayPal
```
