from repository.abstract_repository import AbstractRepository
from repository.dto.manager import ManagerDTO

class ManagerRepository(AbstractRepository[ManagerDTO]):
    def __init__(self) -> None:
        super().__init__(ManagerDTO)
