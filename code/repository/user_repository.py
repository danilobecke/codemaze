from helpers.exceptions import NotFound
from repository.abstract_repository import AbstractRepository
from repository.dto.user import UserDTO

class UserRepository(AbstractRepository):
    def __init__(self):
        super().__init__(UserDTO)

    def find_email(self, email: str) -> UserDTO:
        user = self._session.query(UserDTO).filter_by(email=email).first()
        if user is None:
            raise NotFound()
        return user
