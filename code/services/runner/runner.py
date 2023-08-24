from abc import ABC, abstractmethod
from io import TextIOWrapper

from helpers.commons import file_extension

class Runner(ABC):
    def is_source_code(self, source_path: str) -> bool:
        source_extension = file_extension(source_path)
        return any(source_extension == extension for extension in self.file_extensions)

    @property
    @abstractmethod
    def language_name(self) -> str:
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        pass

    @abstractmethod
    def add_to_sandbox(self, source_path: str, destination_directory: str) -> str:
        pass

    @abstractmethod
    def compile(self, source_path: str, destination_directory: str) -> str:
        pass

    @abstractmethod
    def run(self, executable_path: str, stdin: TextIOWrapper, timeout: float) -> str:
        pass

    @abstractmethod
    def remove_directory(self, path: str) -> None:
        pass
