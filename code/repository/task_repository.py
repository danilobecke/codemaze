from datetime import datetime

from sqlalchemy import select

from repository.abstract_repository import AbstractRepository
from repository.dto.task import TaskDTO

class TaskRepository(AbstractRepository[TaskDTO]):
    def __init__(self) -> None:
        super().__init__(TaskDTO)

    def get_tasks(self, group_id: int, started_only: bool) -> list[TaskDTO]:
        # this is the correct syntax: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#writing-select-statements-for-orm-mapped-classes
        stm = select(TaskDTO).where(TaskDTO.group_id == group_id) # type: ignore
        if started_only is True:
            stm = stm.where(TaskDTO.starts_on <= datetime.now().astimezone())
        stm = stm.order_by(TaskDTO.created_at)
        result: list[TaskDTO] = self._session.scalars(stm).all()
        return result
