import pandas as pd
from typing import Optional, Union, Dict, Any, ClassVar
from pandasai.agent.agent import Agent
from pandasai.schemas.df_config import Config
import hashlib
from pandasai.helpers.dataframe_serializer import (
    DataframeSerializer,
    DataframeSerializerType,
)


class DataFrame(pd.DataFrame):
    """
    PandasAI DataFrame that extends pandas DataFrame with natural language capabilities.

    Attributes:
        name (Optional[str]): Name of the dataframe
        description (Optional[str]): Description of the dataframe
        schema (Optional[Dict]): Schema definition for the dataframe
        config (Config): Configuration settings
    """

    _metadata: ClassVar[list] = [
        "name",
        "description",
        "schema",
        "config",
        "_agent",
        "_column_hash",
    ]

    def __init__(self, *args, **kwargs):
        self.name: Optional[str] = kwargs.pop("name", None)
        self.description: Optional[str] = kwargs.pop("description", None)
        schema: Optional[Dict] = kwargs.pop("schema", None)

        super().__init__(*args, **kwargs)

        if schema is not None:
            self._validate_schema(schema)
        self.schema = schema
        self.config = Config()
        self._agent: Optional[Agent] = None
        self._column_hash = self._calculate_column_hash()

    def _validate_schema(self, schema: Dict) -> None:
        """Validates the provided schema format."""
        if not isinstance(schema, dict):
            raise ValueError("Schema must be a dictionary")

    def __repr__(self) -> str:
        """Return a string representation of the DataFrame."""
        name_str = f"name='{self.name}'" if self.name else ""
        desc_str = f"description='{self.description}'" if self.description else ""
        metadata = ", ".join(filter(None, [name_str, desc_str]))

        print(f"Metadata: {metadata}")

        return f"PandasAI DataFrame({metadata})\n{super().__repr__()}"

    def _calculate_column_hash(self):
        column_string = ",".join(self.columns)
        return hashlib.md5(column_string.encode()).hexdigest()

    @property
    def column_hash(self):
        return self._column_hash

    def chat(self, prompt: str, config: Optional[Union[dict, Config]] = None) -> str:
        """
        Interact with the DataFrame using natural language.

        Args:
            prompt (str): The natural language query or instruction.
            config (Optional[Union[dict, Config]]): Configuration for the chat session.

        Returns:
            str: The response to the prompt.
        """
        if config:
            self.config = Config(**config) if isinstance(config, dict) else config

        if self._agent is None:
            from pandasai.agent.agent import (
                Agent,
            )  # Import here to avoid circular import

            self._agent = Agent([self], config=self.config)

        return self._agent.chat(prompt)

    def follow_up(self, query: str, output_type: Optional[str] = None):
        if self._agent is None:
            raise ValueError(
                "No existing conversation. Please use chat() to start a new conversation."
            )
        return self._agent.follow_up(query, output_type)

    @classmethod
    def from_pandas(
        cls, df: pd.DataFrame, schema: Optional[Dict[str, Any]] = None
    ) -> "DataFrame":
        """
        Create a PandasAI DataFrame from a pandas DataFrame.

        Args:
            df (pd.DataFrame): The pandas DataFrame to convert.
            schema (Optional[Dict[str, Any]]): The schema of the DataFrame.

        Returns:
            DataFrame: A new PandasAI DataFrame instance.
        """
        return cls(df, schema=schema)

    @property
    def rows_count(self) -> int:
        return len(self)

    @property
    def columns_count(self) -> int:
        return len(self.columns)

    def serialize_dataframe(
        self,
        index: int,
        is_direct_sql: bool,
        serializer_type: DataframeSerializerType,
        enforce_privacy: bool,
    ) -> str:
        """
        Serialize DataFrame to string representation.

        Args:
            index (int): Index of the dataframe
            is_direct_sql (bool): Whether the query is direct SQL
            serializer_type (DataframeSerializerType): Type of serializer to use
            enforce_privacy (bool): Whether to enforce privacy
            **kwargs: Additional parameters to pass to pandas to_string method

        Returns:
            str: Serialized string representation of the DataFrame
        """
        return DataframeSerializer().serialize(
            self,
            extras={
                "index": index,
                "type": "pd.DataFrame",
                "is_direct_sql": is_direct_sql,
                "enforce_privacy": enforce_privacy,
            },
            type_=serializer_type,
        )

    def get_head(self):
        return self.head()
