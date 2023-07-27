from repository.abstract_repository import AbstractRepository
from repository.dto.task import TaskDTO

class TaskRepository(AbstractRepository):
    def __init__(self) -> None:
        super().__init__(TaskDTO)

    def get_tasks(self, group_id: int) -> list[TaskDTO]:
        return self._session.query(TaskDTO).filter_by(group_id=group_id).all()
