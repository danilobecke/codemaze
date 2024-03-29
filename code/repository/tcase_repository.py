from sqlalchemy import select

from repository.abstract_repository import AbstractRepository
from repository.dto.test_case import TestCaseDTO

class TCaseRepository(AbstractRepository[TestCaseDTO]):
    def __init__(self) -> None:
        super().__init__(TestCaseDTO)

    def get_tests(self, task_id: int) -> list[TestCaseDTO]:
        stm = select(TestCaseDTO).where(TestCaseDTO.task_id == task_id).order_by(TestCaseDTO.created_at)
        return list(self._session.scalars(stm).all())
