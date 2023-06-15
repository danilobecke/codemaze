from repository.abstract_repository import AbstractRepository
from repository.dto.manager import ManagerDTO

class ManagerRepository(AbstractRepository):
    def __init__(self):
        super().__init__(ManagerDTO)