from typing import Any

from endpoints.models.user import UserVO
from helpers.config import Config
from helpers.exceptions import Forbidden, NotFound, ServerError
from helpers.role import Role
from helpers.unwrapper import unwrap
from repository.dto.manager import ManagerDTO
from repository.dto.student import StudentDTO
from repository.manager_repository import ManagerRepository
from repository.student_repository import StudentRepository
from repository.user_repository import UserRepository

class UserService:
    def __init__(self) -> None:
        self.__user_repository = UserRepository()
        self.__manager_repository = ManagerRepository()
        self.__student_repository = StudentRepository()

    def create_manager(self, name: str, email: str, password: str) -> UserVO:
        adming_dict = dict[str, Any](unwrap(Config.shared)['admin']) # pylint: disable=unsubscriptable-object
        allowed_managers_list = list[str](adming_dict['managers-mail-list'])
        if len(allowed_managers_list) != 0 and email not in allowed_managers_list:
            raise Forbidden()
        dto = ManagerDTO()
        dto.email = email
        dto.name = name
        dto.password = password
        stored_dto = self.__manager_repository.add(dto, raise_unique_violation_error=True)
        vo = UserVO.import_from_dto(stored_dto)
        vo.role = Role.MANAGER
        return vo

    def create_student(self, name: str, email: str, password: str) -> UserVO:
        dto = StudentDTO()
        dto.email = email
        dto.name = name
        dto.password = password
        stored_dto = self.__student_repository.add(dto, raise_unique_violation_error=True)
        vo = UserVO.import_from_dto(stored_dto)
        vo.role = Role.STUDENT
        return vo

    def login(self, email: str, password: str) -> int:
        try:
            dto = self.__user_repository.find_email(email)
            if dto.password != password:
                raise Forbidden()
            return dto.id
        except NotFound as e:
            raise Forbidden() from e
        except Forbidden as e:
            raise e
        except Exception as e:
            raise ServerError() from e

    def get_manager(self, id: int) -> UserVO:
        dto = self.__manager_repository.find(id)
        vo = UserVO.import_from_dto(dto)
        vo.role = Role.MANAGER
        return vo

    def get_student(self, id: int) -> UserVO:
        dto = self.__student_repository.find(id)
        vo = UserVO.import_from_dto(dto)
        vo.role = Role.STUDENT
        return vo
