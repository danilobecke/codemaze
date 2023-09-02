import difflib
from io import TextIOWrapper
import subprocess
import uuid

from endpoints.models.all_tests_vo import AllTestsVO
from endpoints.models.tcase_result_vo import TCaseResultVO
from helpers.commons import file_extension, filename
from helpers.config import Config
from helpers.exceptions import InvalidSourceCode, ExecutionError, CompilationError, ServerError
from helpers.runner_queue_manager import RunnerQueueManager
from helpers.unwrapper import unwrap
from repository.tcase_result_repository import TCaseResultRepository
from repository.dto.test_case_result import TestCaseResultDTO
from services.runner.c_runner import CRunner
from services.runner.python_runner import PythonRunner
from services.runner.runner import Runner

class RunnerService:
    def __init__(self) -> None:
        self.__tcase_result_repository = TCaseResultRepository()
        self.__runners: list[Runner] = [
            CRunner(),
            PythonRunner(),
        ]

    def allowed_languages(self) -> set[str]:
        result: set[str] = set()
        for runner in self.__runners:
            result.add(runner.language_name)
        return result

    def allowed_extensions(self, languages: list[str]) -> set[str]:
        result: set[str] = set()
        for runner in filter(lambda _runner: _runner.language_name in languages , self.__runners):
            result = result.union(runner.file_extensions)
        return result

    def language_with_extension(self, extension: str) -> str | None:
        try:
            return next(runner.language_name for runner in self.__runners if extension in runner.file_extensions)
        except StopIteration:
            return None

    def help_for_language(self, language: str) -> str | None:
        try:
            return next(runner.help for runner in self.__runners if language == runner.language_name)
        except StopIteration:
            return None

    def __execution_command(self, command: str, container: str, interactive: bool = False) -> list[str]:
        return ['docker', 'exec'] + (['-i'] if interactive else []) + [container] + command.split(' ')

    def __add_to_sandbox(self, source_path: str, destination_directory: str, container: str) -> str:
        _filename = filename(source_path)
        dest = f'{destination_directory}/{_filename}'
        subprocess.run(self.__execution_command(f'mkdir {destination_directory}', container), check=True)
        subprocess.run(['docker', 'cp', source_path, f'{container}:sandbox/{dest}'], check=True)
        return dest

    def __compile(self, command: str, container: str) -> None:
        with subprocess.Popen(self.__execution_command(command, container), stdout=subprocess.PIPE,  stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate()
            if stdout.strip():
                raise CompilationError(stdout)
            if stderr.strip():
                raise CompilationError(stderr)

    def __remove_source_path(self, source_path: str, container: str) -> None:
        subprocess.run(self.__execution_command(f'rm {source_path}', container), check=True)

    def __execute(self, command: str, stdin: TextIOWrapper, timeout: float, container: str) -> str:
        with subprocess.Popen(self.__execution_command(command, container, interactive=True), stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate(timeout=timeout)
            if stderr.strip():
                raise ExecutionError(stderr)
            return stdout

    def __remove_directory(self, path: str, container: str) -> None:
        subprocess.run(self.__execution_command(f'rm -rf {path}', container), check=True)

    # pylint: disable=too-many-branches,too-many-statements
    def run(self, path: str, tests: AllTestsVO, result_id: int) -> list[TCaseResultVO]:
        results: list[TCaseResultVO] = []
        try:
            runner = next(_runner for _runner in self.__runners if _runner.is_source_code(path))
            if not RunnerQueueManager.check_container_available(runner):
                RunnerQueueManager.continue_when_available(runner)
                self.run(path, tests, result_id)
            RunnerQueueManager.set_using_container(runner)
            dest = str(uuid.uuid1()) # temp folder
            source_path = self.__add_to_sandbox(path, dest, runner.container_name)
            executable_path = f'{dest}/{str(uuid.uuid1())}'
            self.__compile(runner.compilation_command(source_path, executable_path), runner.container_name)
            self.__remove_source_path(source_path, runner.container_name)
            timeout = float(Config.get('runners.timeout'))
            for test in tests.open_tests + tests.closed_tests:
                dto = TestCaseResultDTO()
                dto.test_case_id = test.id
                dto.result_id = result_id
                try:
                    with open(unwrap(test.input_path), encoding='utf-8') as stdin, open(unwrap(test.output_path), encoding='utf-8') as expected_result:
                        output = self.__execute(runner.execution_command(executable_path), stdin, timeout, runner.container_name)
                        diff = '\n'.join(line for line in difflib.unified_diff(expected_result.readlines(), output.splitlines(), fromfile='expected.out', tofile='result.out', lineterm=''))
                        if len(diff) == 0:
                            dto.success = True
                        else:
                            dto.success = False
                            dto.diff = diff
                except ExecutionError as e:
                    dto.success = False
                    dto.diff = str(e)
                except subprocess.TimeoutExpired:
                    dto.success = False
                    dto.diff = 'Timeout.'
                finally:
                    results.append(TCaseResultVO.import_from_dto(self.__tcase_result_repository.add(dto)))
            self.__remove_directory(dest, runner.container_name)
            RunnerQueueManager.release_container(runner)
            return results
        except StopIteration:
            # no runner found
            # pylint: disable=raise-missing-from
            raise InvalidSourceCode(file_extension(path))
        except CompilationError as e:
            for test in tests.open_tests + tests.closed_tests:
                dto = TestCaseResultDTO()
                dto.test_case_id = test.id
                dto.result_id = result_id
                dto.success = False
                dto.diff = str(e)
                results.append(TCaseResultVO.import_from_dto(self.__tcase_result_repository.add(dto)))
            if runner:
                self.__remove_directory(dest, runner.container_name)
                RunnerQueueManager.release_container(runner)
            return results
        except Exception as e:
            if runner:
                RunnerQueueManager.release_container(runner)
            raise ServerError from e

    def get_test_results(self, result_id: int) -> list[TCaseResultVO]:
        dtos = self.__tcase_result_repository.get_test_results(result_id)
        return list(map(lambda dto: TCaseResultVO.import_from_dto(dto), dtos))
