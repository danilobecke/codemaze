from repository.abstract_repository import AbstractRepository
from repository.dto.student import StudentDTO

class StudentRepository(AbstractRepository[StudentDTO]):
    def __init__(self) -> None:
        super().__init__(StudentDTO)
