from typing import Callable

from endpoints.models.group import GroupVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.tcase_vo import TCaseVO
from endpoints.models.user import UserVO
from helpers.exceptions import Forbidden
from helpers.file import File
from repository.dto.test_case import TestCaseDTO
from repository.tcase_repository import TCaseRepository

class TCaseService:
    def __init__(self) -> None:
        self.__tcase_repository = TCaseRepository()

    def __assert_is_manager(self, user: UserVO, group: GroupVO) -> None:
        if group.manager_id != user.id:
            raise Forbidden()

    def add_test_case(self, user: UserVO, task: TaskVO, group: GroupVO, input_file: File, output_file: File, closed: bool) -> TCaseVO:
        self.__assert_is_manager(user, group)
        dto = TestCaseDTO()
        dto.task_id = task.id
        dto.input_file_path = input_file.save()
        dto.output_file_path = output_file.save()
        dto.closed = closed
        stored = self.__tcase_repository.add(dto)
        return TCaseVO.import_from_dto(stored, is_manager=True)

    def __is_manager(self, user_id: int, group_id: int, user_groups: list[GroupVO]) -> bool:
        groups = list(filter(lambda _group: _group.id == group_id, user_groups))
        if len(groups) == 0:
            raise Forbidden()
        return groups[0].manager_id == user_id

    def __get_test_case(self, id: int, user_id: int, get_task_func: Callable[[int], TaskVO], user_groups: list[GroupVO]) -> TestCaseDTO:
        dto = self.__tcase_repository.find(id)
        task = get_task_func(dto.task_id)
        is_manager = self.__is_manager(user_id, task.group_id, user_groups)
        if dto.closed is True and is_manager is False:
            # Only managers can download closed tests
            raise Forbidden()
        return dto

    def get_test_case_in_path(self, id: int, user_id: int, get_task_func: Callable[[int], TaskVO], user_groups: list[GroupVO]) -> str:
        dto = self.__get_test_case(id, user_id, get_task_func, user_groups)
        return dto.input_file_path

    def get_test_case_out_path(self, id: int, user_id: int, get_task_func: Callable[[int], TaskVO], user_groups: list[GroupVO]) -> str:
        dto = self.__get_test_case(id, user_id, get_task_func, user_groups)
        return dto.output_file_path

    def get_tests(self, user_id: int, task: TaskVO, user_groups: list[GroupVO]) -> list[TCaseVO]:
        is_manager = self.__is_manager(user_id, task.group_id, user_groups)
        dtos = self.__tcase_repository.get_tests(task.id)
        return list(map(lambda dto: TCaseVO.import_from_dto(dto, is_manager), dtos))
