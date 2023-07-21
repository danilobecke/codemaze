from __future__ import annotations

from repository.dto.group_dto import GroupDTO

class GroupVO:
    def __init__(self):
        self.id = -1
        self.active = True
        self.name = ''
        self.code = ''
        self.manager_id = -1

    @staticmethod
    def import_from_dto(dto: GroupDTO) -> GroupVO:
        vo = GroupVO()
        vo.id = dto.id
        vo.active = dto.active
        vo.name = dto.name
        vo.code = dto.code
        vo.manager_id = dto.manager_id
        return vo
