from datetime import datetime
from functools import reduce
from typing import Callable

from endpoints.models.all_tests_vo import AllTestsVO
from endpoints.models.result_vo import ResultVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.tcase_result_vo import TCaseResultVO
from endpoints.models.user import UserVO
from helpers.commons import file_extension
from helpers.exceptions import Forbidden
from helpers.file import File
from helpers.unwrapper import unwrap
from repository.result_repository import ResultRepository
from repository.dto.result import ResultDTO
from services.runner_service import RunnerService

class ResultService:
    def __init__(self, runner_service: RunnerService) -> None:
        self.__runner_service = runner_service
        self.__result_repository = ResultRepository()

    def run(self, user: UserVO, task: TaskVO, tests: AllTestsVO, file: File) -> ResultVO:
        now = datetime.now().astimezone()
        if unwrap(task.starts_on) > now or (task.ends_on is not None and task.ends_on < now):
            raise Forbidden()
        attempt_number = self.__result_repository.get_number_of_results(user.id, task.id) + 1
        if task.max_attempts is not None and attempt_number > task.max_attempts:
            raise Forbidden()
        file_path = file.save(self.__runner_service.allowed_extensions(task.languages))
        dto = ResultDTO()
        dto.correct_open = 0
        dto.correct_closed = 0
        dto.file_path = file_path
        dto.student_id = user.id
        dto.task_id = task.id
        stored = self.__result_repository.add(dto)
        results = self.__runner_service.run(file_path, tests, stored.id)
        open_results = list(filter(lambda result: any(result.test_case_id == test.id for test in tests.open_tests) , results))
        closed_results = list(filter(lambda result: any(result.test_case_id == test.id for test in tests.closed_tests) , results))
        reducer: Callable[[int, TCaseResultVO], int] = lambda current, result: current + (1 if result.success else 0)
        stored.correct_open = reduce(reducer, open_results, 0)
        stored.correct_closed = reduce(reducer, closed_results, 0)
        self.__result_repository.update_session()
        for result in closed_results:
            result.diff = None
        return ResultVO.import_from_dto(stored, attempt_number, open_results, closed_results)

    def get_latest_source_code_name_path(self, task: TaskVO, user_id: int) -> tuple[str, str]:
        dto = self.__result_repository.get_latest_result(user_id, task.id)
        path = dto.file_path
        return ('source' + file_extension(path), path)
