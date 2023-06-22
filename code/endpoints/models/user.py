from typing import Self

from repository.dto.user import UserDTO

class UserVO:
    def __init__(self):
        self.id = -1
        self.email = ''
        self.name = ''
        self.role = ''
        self.token = ''

    @staticmethod
    def import_from_dto(dto: UserDTO) -> Self:
        vo = UserVO()
        vo.id = dto.id
        vo.email = dto.email
        vo.name = dto.name
        return vo