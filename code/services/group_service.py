import secrets
import string
from typing import Callable

from endpoints.models.group import GroupVO
from endpoints.models.join_request import JoinRequestVO
from endpoints.models.user import UserVO
from helpers.exceptions import Internal_UniqueViolation, Forbidden
from repository.group_repository import GroupRepository
from repository.student_group_repository import StudentGroupRepository
from repository.dto.group_dto import GroupDTO
from repository.dto.student_group import StudentGroupDTO

CODE_LENGTH = 6

class GroupService:
    def __init__(self) -> None:
        self.__group_repository = GroupRepository()
        self.__student_group_repository = StudentGroupRepository()

    def __new_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(CODE_LENGTH))

    def create(self, name: str, manager: UserVO) -> GroupVO:
        dto = GroupDTO()
        dto.name = name
        dto.code = self.__new_code()
        dto.manager_id = manager.id
        try:
            stored = self.__group_repository.add(dto, raise_unique_violation_error=True)
            return GroupVO.import_from_dto(stored, manager)
        except Internal_UniqueViolation:
            return self.create(name, manager) # retry if the same code was generated
        except Exception as e:
            raise e

    def add_join_request(self, code: str, student_id: int) -> None:
        group = self.__group_repository.get_group_by_code(code)
        if group.active is False:
            raise Forbidden()
        dto = StudentGroupDTO()
        dto.student_id = student_id
        dto.group_id = group.id
        dto.approved = False
        dto.id = -1 # must be set to respect Base inheritance
        self.__student_group_repository.add(dto, raise_unique_violation_error=True)

    def get_students_with_join_request(self, group_id: int, manager_id: int) -> list[JoinRequestVO]:
        if self.__group_repository.find(group_id).manager_id != manager_id:
            raise Forbidden()
        students = self.__student_group_repository.get_students_with_join_request(group_id)
        return list(map(lambda student: JoinRequestVO.import_from_student(student), students))

    def update_join_request(self, group_id: int, student_id: int, manager_id: int, approved: bool) -> None:
        group = self.__group_repository.find(group_id)
        if group.manager_id != manager_id or group.active is False:
            raise Forbidden()
        if approved:
            self.__student_group_repository.approve_join_request(group_id, student_id)
        else:
            self.__student_group_repository.remove_join_request(group_id, student_id)

    def update_group(self, group_id: int, manager: UserVO, active: bool | None, name: str | None) -> GroupVO:
        dto: GroupDTO = self.__group_repository.find(group_id)
        if dto.manager_id != manager.id:
            raise Forbidden()
        if active is not None:
            dto.active = active
        if name is not None:
            dto.name = name
        self.__group_repository.update_session()
        return GroupVO.import_from_dto(dto, manager)

    def get_all(self, user: UserVO | None, get_manager_with_group: Callable[[int], UserVO]) -> list[GroupVO]:
        dtos: list[GroupDTO]
        if user:
            dtos = self.__student_group_repository.get_groups_for_user(user.id, user.role)
        else:
            dtos = self.__group_repository.find_all()
        return list(map(lambda dto: GroupVO.import_from_dto(dto, get_manager_with_group(dto.manager_id)), dtos))

    def get_group(self, id: int, get_manager_with_group: Callable[[int], UserVO]) -> GroupVO:
        dto = self.__group_repository.find(id)
        return GroupVO.import_from_dto(dto, get_manager_with_group(dto.manager_id))

    def get_students_of_group(self, id: int, manager_id: int) -> list[UserVO]:
        if self.__group_repository.find(id).manager_id != manager_id:
            raise Forbidden()
        students = self.__student_group_repository.get_students_with_join_request(id, approved=True)
        return list(map(lambda student: UserVO.import_from_dto(student), students))
