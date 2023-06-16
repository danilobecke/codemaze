from repository.dto.group import GroupDTO
from typing import Self

class GroupVO:
    def __init__(self):
        self.id = -1
        self.active = True
        self.name = ''
        self.code = ''
        self.manager_id = -1

    @staticmethod
    def import_from_dto(dto: GroupDTO) -> Self:
        vo = GroupVO()
        vo.id = dto.id
        vo.active = dto.active
        vo.name = dto.name
        vo.code = dto.code
        vo.manager_id = dto.manager_id
        return vo