import string
import secrets
from repository.group_repository import GroupRepository
from repository.dto.group import GroupDTO
from endpoints.models.group import GroupVO
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
            self.create(name, manager_id) # retry if the same code was generated
        except Exception as e:
            raise e

