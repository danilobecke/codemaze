from repository.abstract_repository import AbstractRepository
from repository.dto.test_case import TestCaseDTO

class TCaseRepository(AbstractRepository):
    def __init__(self):
        super().__init__(TestCaseDTO)
