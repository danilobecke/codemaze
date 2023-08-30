from abc import ABC, abstractmethod

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

    @property
    @abstractmethod
    def container_name(self) -> str:
        pass

    @abstractmethod
    def compilation_command(self, source_path: str, executable: str) -> str:
        pass

    @abstractmethod
    def execution_command(self, executable_path: str) -> str:
        pass
