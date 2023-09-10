from __future__ import annotations

from repository.dto.user_dto import UserDTO

class JoinRequestVO:
    def __init__(self) -> None:
        self.id = -1
        self.student = ""

    @staticmethod
    def import_from_student(dto: UserDTO) -> JoinRequestVO:
        vo = JoinRequestVO()
        vo.id = dto.id
        vo.student = dto.name
        return vo
