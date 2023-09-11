from sqlalchemy import select

from helpers.exceptions import NotFound
from helpers.role import Role
from repository.abstract_repository import AbstractRepository
from repository.dto.user_dto import UserDTO

class UserRepository(AbstractRepository[UserDTO]):
    def __init__(self) -> None:
        super().__init__(UserDTO)

    def find_email(self, email: str) -> UserDTO:
        stm = select(UserDTO).where(UserDTO.email == email)
        user = self._session.scalars(stm).first()
        if user is None:
            raise NotFound()
        return user

    def find_user_with_role(self, id: int, role: Role | None) -> UserDTO:
        stm = select(UserDTO).where(UserDTO.id == id)
        if role is not None:
            stm = stm.where(UserDTO.role == role)
        user = self._session.scalars(stm).first()
        if user is None:
            raise NotFound()
        return user
