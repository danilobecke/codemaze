from endpoints.models.group import GroupVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.tcase_vo import TCaseVO
from endpoints.models.user import UserVO
from helpers.exceptions import Forbidden
from helpers.file import File
from repository.dto.test_case import TestCaseDTO
from repository.tcase_repository import TCaseRepository

class TCaseService:
    def __init__(self):
        self.__tcase_repository = TCaseRepository()

    def __assert_is_manager(self, user: UserVO, group: GroupVO):
        if group.manager_id != user.id:
            raise Forbidden()

    # pylint: disable=too-many-arguments
    def add_test_case(self, user: UserVO, task: TaskVO, group: GroupVO, input_file: File, output_file: File, closed: bool) -> TCaseVO:
        self.__assert_is_manager(user, group)
        dto = TestCaseDTO()
        dto.task_id = task.id
        dto.input_file_path = input_file.save()
        dto.output_file_path = output_file.save()
        dto.closed = closed
        stored = self.__tcase_repository.add(dto)
        return TCaseVO.import_from_dto(stored)
