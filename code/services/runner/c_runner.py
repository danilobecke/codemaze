from io import TextIOWrapper
import subprocess
import uuid

from helpers.commons import filename
from helpers.exceptions import CompilationError, ExecutionError
from services.runner.runner import Runner

class CRunner(Runner):
    def __init__(self) -> None:
        self.__container = 'gcc-container'

    @property
    def language_name(self) -> str:
        return 'c'

    @property
    def file_extensions(self) -> list[str]:
        return ['.c']

    def add_to_sandbox(self, source_path: str, destination_directory: str) -> str:
        _filename = filename(source_path)
        dest = f'{destination_directory}/{_filename}'
        subprocess.run(self.__exec(f'mkdir {destination_directory}'), check=True)
        subprocess.run(['docker', 'cp', source_path, f'{self.__container}:sandbox/{dest}'], check=True)
        return dest

    def __exec(self, command: str, interactive: bool = False) -> list[str]:
        return ['docker', 'exec'] + (['-i'] if interactive else []) + [self.__container] + command.split(' ')

    def compile(self, source_path: str, destination_directory: str) -> str:
        executable = f'{destination_directory}/{str(uuid.uuid1())}'
        with subprocess.Popen(self.__exec(f'gcc -Wall -g -lm -o {executable} {source_path}'), stdout=subprocess.PIPE,  stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate()
            if stdout.strip():
                raise CompilationError(stdout)
            if stderr.strip():
                raise CompilationError(stderr)
            subprocess.run(self.__exec(f'rm {source_path}'), check=True)
            return executable

    def run(self, executable_path: str, stdin: TextIOWrapper, timeout: float) -> str:
        with subprocess.Popen(self.__exec(f'./{executable_path}', interactive=True), stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate(timeout=timeout)
            if stderr.strip():
                raise ExecutionError(stderr)
            return stdout

    def remove_directory(self, path: str) -> None:
        subprocess.run(self.__exec(f'rm -rf {path}'), check=True)
