from helpers.exceptions import NotFound
from repository.abstract_repository import AbstractRepository
from repository.dto.user_dto import UserDTO

class UserRepository(AbstractRepository):
    def __init__(self) -> None:
        super().__init__(UserDTO)

    def find_email(self, email: str) -> UserDTO:
        user: UserDTO | None = self._session.query(UserDTO).filter_by(email=email).first()
        if user is None:
            raise NotFound()
        return user
