from sqlalchemy import select

from helpers.exceptions import NotFound
from repository.abstract_repository import AbstractRepository
from repository.dto.group_dto import GroupDTO

# pylint: disable=singleton-comparison
class GroupRepository(AbstractRepository[GroupDTO]):
    def __init__(self) -> None:
        super().__init__(GroupDTO)

    def get_group_by_code(self, code: str) -> GroupDTO:
        group = self._session.scalars(select(GroupDTO).where(GroupDTO.code == code)).first()
        if not group:
            raise NotFound()
        return group
