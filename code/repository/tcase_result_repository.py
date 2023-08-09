from repository.abstract_repository import AbstractRepository
from repository.dto.test_case_result import TestCaseResultDTO

class TCaseResultRepository(AbstractRepository[TestCaseResultDTO]):
    def __init__(self) -> None:
        super().__init__(TestCaseResultDTO)
