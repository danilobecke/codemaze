from repository.abstract_repository import AbstractRepository
from repository.dto.test_case import TestCaseDTO

class TCaseRepository(AbstractRepository[TestCaseDTO]):
    def __init__(self) -> None:
        super().__init__(TestCaseDTO)

    def get_tests(self, task_id: int) -> list[TestCaseDTO]:
        result: list[TestCaseDTO] = self._session.query(TestCaseDTO).filter_by(task_id=task_id).order_by(TestCaseDTO.created_at).all()
        return result
