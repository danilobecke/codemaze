from helpers.config import Config
from services.runner.runner import Runner

class CRunner(Runner):
    def __init__(self) -> None:
        self.__gcc_params = str(Config.get('runners.c.gcc-parameters'))

    @property
    def language_name(self) -> str:
        return 'c'

    @property
    def file_extensions(self) -> list[str]:
        return ['.c']

    @property
    def help(self) -> str:
        command = self.__gcc_command('executable', 'source.c')
        return f'Compilation command: {command}'

    @property
    def container_name(self) -> str:
        return 'gcc-container'

    def __gcc_command(self, executable: str, source_path: str) -> str:
        gcc_options = str(self.__gcc_params)
        return f'gcc {gcc_options} -o {executable} {source_path}'

    def compilation_command(self, source_path: str, executable: str) -> str:
        return self.__gcc_command(executable, source_path)

    def execution_command(self, executable_path: str) -> str:
        return f'./{executable_path}'
