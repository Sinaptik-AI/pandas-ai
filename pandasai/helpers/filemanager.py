import os
from abc import ABC, abstractmethod

from pandasai.helpers.path import find_project_root


class FileManager(ABC):
    """Abstract base class for file loaders, supporting local and remote backends."""

    @abstractmethod
    def load(self, file_path: str) -> str:
        """Reads the content of a file."""
        pass

    @abstractmethod
    def load_binary(self, file_path: str) -> bytes:
        """Reads the content of a file as bytes."""
        pass

    @abstractmethod
    def write(self, file_path: str, content: str) -> None:
        """Writes content to a file."""
        pass

    @abstractmethod
    def write_binary(self, file_path: str, content: bytes) -> None:
        """Writes binary content to a file."""
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """Checks if a file or directory exists."""
        pass

    @abstractmethod
    def mkdir(self, dir_path: str) -> None:
        """Creates a directory if it doesn't exist."""
        pass

    @abstractmethod
    def abs_path(self, file_path: str) -> str:
        """Returns the absolute path of {file_path}"""
        pass


class DefaultFileManager(FileManager):
    """Local file system implementation of FileLoader."""

    def __init__(self):
        self.base_path = os.path.join(find_project_root(), "datasets")

    def load(self, file_path: str) -> str:
        with open(self.abs_path(file_path), "r", encoding="utf-8") as f:
            return f.read()

    def load_binary(self, file_path: str) -> bytes:
        with open(self.abs_path(file_path), "rb") as f:
            return f.read()

    def write(self, file_path: str, content: str) -> None:
        with open(self.abs_path(file_path), "w", encoding="utf-8") as f:
            f.write(content)

    def write_binary(self, file_path: str, content: bytes) -> None:
        with open(self.abs_path(file_path), "wb") as f:
            f.write(content)

    def exists(self, file_path: str) -> bool:
        return os.path.exists(self.abs_path(file_path))

    def mkdir(self, dir_path: str) -> None:
        os.makedirs(self.abs_path(dir_path), exist_ok=True)

    def abs_path(self, file_path: str) -> str:
        return os.path.join(self.base_path, file_path)
