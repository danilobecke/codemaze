from sqlalchemy import select, func, and_

from helpers.unwrapper import unwrap
from repository.abstract_repository import AbstractRepository
from repository.dto.result import ResultDTO

# pylint: disable=not-callable
class ResultRepository(AbstractRepository[ResultDTO]):
    def __init__(self) -> None:
        super().__init__(ResultDTO)

    def get_number_of_results(self, user_id: int, task_id: int) -> int:
        stm = select(func.count()).select_from(ResultDTO)\
            .where(and_(ResultDTO.student_id == user_id, ResultDTO.task_id == task_id))
        result = self._session.scalar(stm)
        return unwrap(result)
