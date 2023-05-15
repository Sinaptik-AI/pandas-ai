Usage
=====

Installation
------------

To use Lumache, first install it using pip:

```console
(.venv) $ pip install lumache
```

Creating recipes
----------------

To retrieve a list of random ingredients, you can use the
`lumache.get_random_ingredients()` function:

::: pandasai.lumache.get_random_ingredients
    options:
      show_root_heading: true

<br>

The `kind` parameter should be either `"meat"`, `"fish"`, or `"veggies"`.
Otherwise, [`get_random_ingredients`][lumache.get_random_ingredients] will raise an exception [`lumache.InvalidKindError`](/api#lumache.InvalidKindError).

For example:

```python
>>>
from pandasai import lumache
>>> lumache.get_random_ingredients()
['shells', 'gorgonzola', 'parsley']
```
