from typing import Callable

from endpoints.models.group import GroupVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.tcase_vo import TCaseVO
from helpers.exceptions import Forbidden
from helpers.file import File
from repository.dto.test_case import TestCaseDTO
from repository.tcase_repository import TCaseRepository

class TCaseService:
    def __init__(self) -> None:
        self.__tcase_repository = TCaseRepository()

    def add_test_case(self, task: TaskVO, input_file: File, output_file: File, closed: bool) -> TCaseVO:
        dto = TestCaseDTO()
        dto.task_id = task.id
        dto.input_file_path = input_file.save()
        dto.output_file_path = output_file.save()
        dto.closed = closed
        stored = self.__tcase_repository.add(dto)
        return TCaseVO.import_from_dto(stored, is_manager=True)

    def __is_manager(self, user_id: int, group_id: int, user_groups: list[GroupVO]) -> bool:
        group = next(filter(lambda _group: _group.id == group_id, user_groups))
        return group.manager_id == user_id

    def __get_test_case(self, id: int, user_id: int, get_task_func: Callable[[int, int, list[GroupVO]], TaskVO], user_groups: list[GroupVO]) -> TestCaseDTO:
        dto = self.__tcase_repository.find(id)
        task = get_task_func(dto.task_id, user_id, user_groups)
        is_manager = self.__is_manager(user_id, task.group_id, user_groups)
        if dto.closed is True and is_manager is False:
            # Only managers can download closed tests
            raise Forbidden()
        return dto

    def get_test_case_in_path(self, id: int, user_id: int, get_task_func: Callable[[int, int, list[GroupVO]], TaskVO], user_groups: list[GroupVO]) -> str:
        dto = self.__get_test_case(id, user_id, get_task_func, user_groups)
        return dto.input_file_path

    def get_test_case_out_path(self, id: int, user_id: int, get_task_func: Callable[[int, int, list[GroupVO]], TaskVO], user_groups: list[GroupVO]) -> str:
        dto = self.__get_test_case(id, user_id, get_task_func, user_groups)
        return dto.output_file_path

    def get_tests(self, user_id: int, task: TaskVO, user_groups: list[GroupVO]) -> list[TCaseVO]:
        is_manager = self.__is_manager(user_id, task.group_id, user_groups)
        dtos = self.__tcase_repository.get_tests(task.id)
        return list(map(lambda dto: TCaseVO.import_from_dto(dto, is_manager), dtos))

    def delete_test(self, id: int, user_id: int, get_task_func: Callable[[int, int, list[GroupVO]], TaskVO], user_groups: list[GroupVO]) -> None:
        dto = self.__tcase_repository.find(id)
        get_task_func(dto.task_id, user_id, user_groups) # if has access to the task, is the manager - this is a manager only function
        self.__tcase_repository.delete(id)
