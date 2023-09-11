from endpoints.models.user import UserVO
from helpers.config import Config
from helpers.exceptions import Forbidden, NotFound, ServerError
from helpers.role import Role
from repository.user_repository import UserRepository
from repository.dto.user_dto import UserDTO

class UserService:
    def __init__(self) -> None:
        self.__user_repository = UserRepository()

    def __create_user(self, name: str, email: str, password: str, role: Role) -> UserVO:
        dto = UserDTO()
        dto.email = email
        dto.name = name
        dto.password = password
        dto.role = role
        stored_dto = self.__user_repository.add(dto, raise_unique_violation_error=True)
        return UserVO.import_from_dto(stored_dto)

    def create_manager(self, name: str, email: str, password: str) -> UserVO:
        allowed_managers_list = list[str](Config.get('admin.managers-mail-list'))
        if len(allowed_managers_list) != 0 and email not in allowed_managers_list:
            raise Forbidden()
        return self.__create_user(name, email, password, Role.MANAGER)

    def create_student(self, name: str, email: str, password: str) -> UserVO:
        return self.__create_user(name, email, password, Role.STUDENT)

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

    def get_user_with_role(self, id: int, role: Role | None) -> UserVO:
        dto = self.__user_repository.find_user_with_role(id, role)
        return UserVO.import_from_dto(dto)
