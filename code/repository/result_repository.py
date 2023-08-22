from sqlalchemy import select, func, and_, desc

from helpers.exceptions import NotFound
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

    def get_latest_result(self, user_id: int, task_id: int) -> ResultDTO:
        stm = select(ResultDTO).where(and_(ResultDTO.student_id == user_id, ResultDTO.task_id == task_id)).order_by(desc(ResultDTO.created_at))
        result = self._session.scalars(stm).first()
        if result is None:
            raise NotFound()
        return result

    def get_results_for_task(self, task_id: int) -> list[ResultDTO]:
        stm = select(ResultDTO).where(ResultDTO.task_id == task_id).order_by(ResultDTO.created_at)
        return list(self._session.scalars(stm).all())
