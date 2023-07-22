from repository.abstract_repository import AbstractRepository
from repository.dto.task import TaskDTO

class TaskRepository(AbstractRepository):
    def __init__(self):
        super().__init__(TaskDTO)
