from repository.abstract_repository import AbstractRepository
from repository.dto.group import GroupDTO

class GroupRepository(AbstractRepository):
    def __init__(self):
        super().__init__(GroupDTO)