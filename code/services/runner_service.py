import difflib
import uuid

from endpoints.models.all_tests_vo import AllTestsVO
from endpoints.models.tcase_result_vo import TCaseResultVO
from helpers.commons import file_extension
from helpers.exceptions import InvalidSourceCode, ExecutionError, CompilationError, ServerError
from helpers.unwrapper import unwrap
from repository.tcase_result_repository import TCaseResultRepository
from repository.dto.test_case_result import TestCaseResultDTO
from services.runner.c_runner import CRunner
from services.runner.runner import Runner

class RunnerService:
    def __init__(self) -> None:
        self.__tcase_result_repository = TCaseResultRepository()
        self.__runners: list[Runner] = [
            CRunner(),
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

    def run(self, path: str, tests: AllTestsVO, result_id: int) -> list[TCaseResultVO]:
        results: list[TCaseResultVO] = []
        try:
            runner = next(_runner for _runner in self.__runners if _runner.is_source_code(path))
            dest = str(uuid.uuid1())
            source_path = runner.add_to_sandbox(path, dest)
            executable_path = runner.compile(source_path, dest)
            for test in tests.open_tests + tests.closed_tests:
                dto = TestCaseResultDTO()
                dto.test_case_id = test.id
                dto.result_id = result_id
                try:
                    with open(unwrap(test.input_path), encoding='utf-8') as stdin, open(unwrap(test.output_path), encoding='utf-8') as expected_result:
                        output = runner.run(executable_path, stdin, timeout=2)
                        diff = '\n'.join(line for line in difflib.unified_diff(expected_result.readlines(), output.splitlines(), fromfile='expected.out', tofile='result.out', lineterm=''))
                        if len(diff) == 0:
                            dto.success = True
                        else:
                            dto.success = False
                            dto.diff = diff
                except ExecutionError as e:
                    dto.success = False
                    dto.diff = str(e)
                except TimeoutError:
                    dto.success = False
                    dto.diff = 'Timeout.'
                finally:
                    results.append(TCaseResultVO.import_from_dto(self.__tcase_result_repository.add(dto)))
            runner.remove_directory(dest)
            return results
        except StopIteration:
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
            return results
        except Exception as e:
            raise ServerError from e
