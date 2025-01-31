import os
from abc import ABC, abstractmethod
from pandasai.helpers.path import find_project_root

class FileLoader(ABC):
    """Abstract base class for file loaders, supporting local and remote backends."""

    @abstractmethod
    def load(self, file_path: str) -> str:
        """Reads the content of a file."""
        pass

    @abstractmethod
    def write(self, file_path: str, content: str) -> None:
        """Writes content to a file."""
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """Checks if a file or directory exists."""
        pass

    @abstractmethod
    def mkdir(self, dir_path: str) -> None:
        """Creates a directory if it doesn't exist."""
        pass


class DefaultFileLoader(FileLoader):
    """Local file system implementation of FileLoader."""

    def __init__(self):
        self.base_path = find_project_root()

    def load(self, file_path: str) -> str:
        full_path = self.base_path / file_path
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def write(self, file_path: str, content: str) -> None:
        full_path = self.base_path / file_path
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def exists(self, file_path: str) -> bool:
        """Checks if a file or directory exists."""
        full_path = self.base_path / file_path
        return os.path.exists(full_path)

    def mkdir(self, dir_path: str) -> None:
        """Creates a directory if it doesn't exist."""
        full_path = self.base_path / dir_path
        os.makedirs(full_path, exist_ok=True)