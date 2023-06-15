from repository.abstract_repository import AbstractRepository
from repository.dto.student import StudentDTO

class StudentRepository(AbstractRepository):
    def __init__(self):
        super().__init__(StudentDTO)