from typing import Self

from repository.dto.user import UserDTO

class JoinRequestVO:
    def __init__(self):
        self.id = -1
        self.student = ""

    @staticmethod
    def import_from_student(dto: UserDTO) -> Self:
        vo = JoinRequestVO()
        vo.id = dto.id
        vo.student = dto.name
        return vo