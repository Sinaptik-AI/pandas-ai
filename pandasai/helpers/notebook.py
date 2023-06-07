""" Helper Module to Handle Jupyter Notebook
This module contains helper functions to interact with Jupyter Notebook Functionalities.

"""

from IPython import get_ipython


class Notebook:

    """Baseclass to implement Notebook helper functions"""

    def in_notebook(self) -> bool:
        """
        Checks whether the code is running inside a notebook environment.

        Returns (bool): True if the code is running inside a Jupyter notebook,
        False otherwise.
        """
        try:
            if "IPKernelApp" not in get_ipython().config:
                return False
        except (ImportError, AttributeError):
            return False
        return True

    def create_new_cell(self, contents: str) -> None:
        """
        Creates a new code cell in the Jupyter notebook and populates
        it with the specified contents.
        Args:
            contents (str): The contents to be added to the new code cell.

        ImportError:
            If the IPython module is not installed.

        AttributeError:
            If the 'get_ipython()' call raises an AttributeError, which can happen
            if the code is not running inside a Jupyter notebook.

        Returns: None

        """

        payload = {"source": "set_next_input", "text": contents, "replace": False}
        try:
            get_ipython().payload_manager.write_payload(payload, single=False)
        except (ImportError, AttributeError) as exception:
            raise exception
