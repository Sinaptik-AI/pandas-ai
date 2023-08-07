"""
Base connector class to be extended by all connectors.
"""

from abc import ABC, abstractmethod


class BaseConnector(ABC):
    """
    Base connector class to be extended by all connectors.
    """

    _config = None

    def __init__(self, config):
        """
        Initialize the connector with the given configuration.

        Args:
            config (dict): The configuration for the connector.
        """
        self._config = config

    @abstractmethod
    def head(self):
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the data source.
        """
        pass

    @abstractmethod
    def execute(self):
        """
        Execute the given query on the data source that the connector is connected to.
        """
        pass
