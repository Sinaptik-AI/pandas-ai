""" Base class to implement a new Prompt
In order to better handle the instructions, this prompt module is written.
"""

from pandasai.exceptions import MethodNotImplementedError


class Prompt:
    """Base class to implement a new Prompt"""

    text = None
    _args = {}

    def __init__(self, **kwargs):
        """
        __init__ method of Base class of Prompt Module
        Args:
            **kwargs: Inferred Keyword Arguments
        """
        if kwargs:
            self._args = kwargs

    def _generate_dataframes(self, dfs):
        """
        Generate the dataframes metadata
        Args:
            dfs: List of Dataframes
        """
        dataframes = []
        for index, df in enumerate(dfs, start=1):
            description = "Dataframe "
            if df.name is not None:
                description += f"{df.name} (dfs[{index-1}])"
            else:
                description += f"dfs[{index-1}]"
            description += (
                f", with {df.rows_count} rows and {df.columns_count} columns."
            )
            if df.description is not None:
                description += f"\nDescription: {df.description}"
            description += f"""
This is the metadata of the dataframe dfs[{index-1}]:
{df.head_csv}"""  # noqa: E501
            dataframes.append(description)

        return "\n\n".join(dataframes)

    def set_var(self, var, value):
        if var == "dfs":
            self._args["dataframes"] = self._generate_dataframes(value)
        self._args[var] = value

    def to_string(self):
        if self.text is None:
            raise MethodNotImplementedError

        return self.text.format(**self._args)

    def __str__(self):
        return self.to_string()
