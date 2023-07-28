from repository.abstract_repository import AbstractRepository
from repository.dto.test_case import TestCaseDTO

class TCaseRepository(AbstractRepository[TestCaseDTO]):
    def __init__(self) -> None:
        super().__init__(TestCaseDTO)
