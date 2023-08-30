from services.runner.runner import Runner

class PythonRunner(Runner):
    @property
    def language_name(self) -> str:
        return 'python'

    @property
    def file_extensions(self) -> list[str]:
        return ['.py']

    @property
    def help(self) -> str:
        return 'Python version: 3.11' # defined on compose.yml

    @property
    def container_name(self) -> str:
        return 'python-container'

    def compilation_command(self, source_path: str, executable: str) -> str:
        return f'cp {source_path} {executable}'

    def execution_command(self, executable_path: str) -> str:
        return f'python {executable_path}'
