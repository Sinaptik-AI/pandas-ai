"""Callback Handler that writes to a file."""
from typing import TextIO, cast
from .base import BaseCallback


class FileCallback(BaseCallback):
    """Callback Handler that writes to a file."""

    def __init__(self, filename: str, mode: str = "w") -> None:
        """Initialize callback handler."""
        self.file = cast(TextIO, open(filename, mode))

    def __del__(self) -> None:
        """Destructor to clean up when done."""
        self.file.close()

    def on_code(self, response: str):
        """Write the code response to file"""
        self.file.write(response)
