from sqlalchemy import select

from repository.abstract_repository import AbstractRepository
from repository.dto.test_case_result import TestCaseResultDTO

class TCaseResultRepository(AbstractRepository[TestCaseResultDTO]):
    def __init__(self) -> None:
        super().__init__(TestCaseResultDTO)

    def get_test_results(self, result_id: int) -> list[TestCaseResultDTO]:
        stm = select(TestCaseResultDTO).where(TestCaseResultDTO.result_id == result_id).order_by(TestCaseResultDTO.created_at)
        return list(self._session.scalars(stm).all())
