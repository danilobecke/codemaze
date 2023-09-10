from sqlalchemy import select, insert, Select

from helpers.exceptions import NotFound
from repository.abstract_repository import AbstractRepository
from repository.dto.manager import ManagerDTO
from repository.dto.student import StudentDTO
from repository.dto.user_dto import UserDTO

class UserRepository(AbstractRepository[UserDTO]):
    def __init__(self) -> None:
        super().__init__(UserDTO)

    def model_or_not_found(self, stm: Select[tuple[UserDTO]]) -> UserDTO:
        model = self._session.scalars(stm).first()
        if not model:
            raise NotFound()
        return model

    def find_email(self, email: str) -> UserDTO:
        stm = select(UserDTO).where(UserDTO.email == email)
        return self.model_or_not_found(stm)

    def add_manager(self, dto: UserDTO) -> UserDTO:
        user = super().add(dto, raise_unique_violation_error=True)
        stm = insert(ManagerDTO).values(id=user.id)
        self._session.execute(stm)
        self.update_session()
        return user

    def add_student(self, dto: UserDTO) -> UserDTO:
        user = super().add(dto, raise_unique_violation_error=True)
        stm = insert(StudentDTO).values(id=user.id)
        self._session.execute(stm)
        self.update_session()
        return user

    def find_manager(self, id: int) -> UserDTO:
        stm = select(UserDTO)\
            .join(ManagerDTO, UserDTO.id == ManagerDTO.id)\
            .where(ManagerDTO.id == id)
        return self.model_or_not_found(stm)

    def find_student(self, id: int) -> UserDTO:
        stm = select(UserDTO)\
            .join(StudentDTO, UserDTO.id == StudentDTO.id)\
            .where(StudentDTO.id == id)
        return self.model_or_not_found(stm)
