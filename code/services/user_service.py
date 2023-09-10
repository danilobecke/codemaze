from endpoints.models.user import UserVO
from helpers.config import Config
from helpers.exceptions import Forbidden, NotFound, ServerError
from helpers.role import Role
from repository.dto.user_dto import UserDTO
from repository.user_repository import UserRepository

class UserService:
    def __init__(self) -> None:
        self.__user_repository = UserRepository()

    def create_manager(self, name: str, email: str, password: str) -> UserVO:
        allowed_managers_list = list[str](Config.get('admin.managers-mail-list'))
        if len(allowed_managers_list) != 0 and email not in allowed_managers_list:
            raise Forbidden()
        dto = UserDTO()
        dto.email = email
        dto.name = name
        dto.password = password
        stored_dto = self.__user_repository.add_manager(dto)
        vo = UserVO.import_from_dto(stored_dto)
        vo.role = Role.MANAGER
        return vo

    def create_student(self, name: str, email: str, password: str) -> UserVO:
        dto = UserDTO()
        dto.email = email
        dto.name = name
        dto.password = password
        stored_dto = self.__user_repository.add_student(dto)
        vo = UserVO.import_from_dto(stored_dto)
        vo.role = Role.STUDENT
        return vo

    def login(self, email: str, password: str) -> int:
        try:
            dto = self.__user_repository.find_email(email)
            if not dto.authenticate(password):
                raise Forbidden()
            return dto.id
        except NotFound as e:
            raise Forbidden() from e
        except Forbidden as e:
            raise e
        except Exception as e:
            raise ServerError() from e

    def get_manager(self, id: int) -> UserVO:
        dto = self.__user_repository.find_manager(id)
        vo = UserVO.import_from_dto(dto)
        vo.role = Role.MANAGER
        return vo

    def get_student(self, id: int) -> UserVO:
        dto = self.__user_repository.find_student(id)
        vo = UserVO.import_from_dto(dto)
        vo.role = Role.STUDENT
        return vo
