from __future__ import annotations

from endpoints.models.user import UserVO
from helpers.unwrapper import unwrap
from repository.dto.group_dto import GroupDTO

class GroupVO:
    @property
    def manager_id(self) -> int:
        return unwrap(self.manager).id

    def __init__(self) -> None:
        self.id = -1
        self.active = True
        self.name = ''
        self.code = ''
        self.manager: UserVO | None = None

    @staticmethod
    def import_from_dto(dto: GroupDTO, manager: UserVO) -> GroupVO:
        vo = GroupVO()
        vo.id = dto.id
        vo.active = dto.active
        vo.name = dto.name
        vo.code = dto.code
        vo.manager = manager
        return vo
