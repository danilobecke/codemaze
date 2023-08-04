from sqlalchemy import select

from helpers.exceptions import NotFound
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
