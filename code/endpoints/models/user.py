from __future__ import annotations

from helpers.role import Role
from repository.dto.user_dto import UserDTO

class UserVO:
    def __init__(self) -> None:
        self.id = -1
        self.email = ''
        self.name = ''
        self.role = Role.STUDENT
        self.token = ''

    @staticmethod
    def import_from_dto(dto: UserDTO) -> UserVO:
        vo = UserVO()
        vo.id = dto.id
        vo.email = dto.email
        vo.name = dto.name
        return vo
