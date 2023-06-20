import string
import secrets
from repository.group_repository import GroupRepository
from repository.dto.group import GroupDTO
from endpoints.models.group import GroupVO
from endpoints.models.join_request import JoinRequestVO
from endpoints.models.user import UserVO
from helpers.exceptions import *

class GroupService:
    __CODE_LENGTH = 6

    def __init__(self):
        self.__group_repository = GroupRepository()

    def __new_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(GroupService.__CODE_LENGTH))

    def create(self, name: str, manager_id: int) -> GroupVO:
        dto = GroupDTO()
        dto.name = name
        dto.code = self.__new_code()
        dto.manager_id = manager_id
        try:
            stored = self.__group_repository.add(dto, raise_unique_violation_error=True)
            return GroupVO.import_from_dto(stored)
        except Internal_UniqueViolation:
            return self.create(name, manager_id) # retry if the same code was generated
        except Exception as e:
            raise e

    def add_join_request(self, code: str, student_id: int):
        self.__group_repository.add_join_request(code, student_id)

    def get_students_with_join_request(self, group_id: int, manager_id: int) -> list[JoinRequestVO]:
        if self.__group_repository.find(group_id).manager_id != manager_id:
            raise Forbidden()
        students = self.__group_repository.get_students_with_join_request(group_id)
        return list(map(lambda student: JoinRequestVO.import_from_student(student), students))

    def update_join_request(self, group_id: int, student_id: int, manager_id: int, approved: bool):
        if self.__group_repository.find(group_id).manager_id != manager_id:
            raise Forbidden()
        if approved:
            self.__group_repository.approve_join_request(group_id, student_id)
        else:
            self.__group_repository.remove_join_request(group_id, student_id)

    def update_group_active(self, group_id: int, manager_id: int, active: bool):
        dto: GroupDTO = self.__group_repository.find(group_id)
        if dto.manager_id != manager_id:
            raise Forbidden()
        dto.active = active
        self.__group_repository.update_session()
    
    def get_all(self, user: UserVO | None) -> list[GroupVO]:
        dtos: list[GroupDTO]
        if user:
            dtos = self.__group_repository.get_groups_for_user(user.id, user.role)
        else:
            dtos = self.__group_repository.find_all()
        return list(map(lambda dto: GroupVO.import_from_dto(dto), dtos))
    
    def get_group(self, id: int) -> GroupVO:
        dto = self.__group_repository.find(id)
        return GroupVO.import_from_dto(dto)

    def get_students_of_group(self, id: int, manager_id: int) -> list[UserVO]:
        if self.__group_repository.find(id).manager_id != manager_id:
            raise Forbidden()
        students = self.__group_repository.get_students_with_join_request(id, approved=True)
        return list(map(lambda student: UserVO.import_from_dto(student), students))
