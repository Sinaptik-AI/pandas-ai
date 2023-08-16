# Cache

PandasAI uses a cache to store the results of previous queries. This is useful for two reasons:

1. It allows the user to quickly retrieve the results of a query without having to wait for the model to generate a response.
2. It cuts down on the number of API calls made to the model, reducing the cost of using the model.

The cache is stored in a file called `cache.db` in the `/cache` directory of the project. The cache is a SQLite database, and can be viewed using any SQLite client. The file will be created automatically when the first query is made.

## Disabling the cache

The cache can be disabled by setting the `enable_cache` parameter to `False` when creating the `PandasAI` object:

```python
df = SmartDataframe('data.csv', {"enable_cache": False})
```

By default, the cache is enabled.

## Clearing the cache

The cache can be cleared by deleting the `cache.db` file. The file will be recreated automatically when the next query is made. Alternatively, the cache can be cleared by calling the `clear_cache()` method on the `PandasAI` object:

```python
import pandas_ai as pai
pai.clear_cache()
```
