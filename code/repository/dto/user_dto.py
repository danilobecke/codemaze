from bcrypt import hashpw, checkpw, gensalt
from sqlalchemy import Integer, Sequence, String
from sqlalchemy.orm import mapped_column, Mapped

from repository.base import Base

class UserDTO(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, Sequence('sq_user_pk'), primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    _password: Mapped[str] = mapped_column('password', String)
    name: Mapped[str]

    @property
    def password(self) -> str:
        raise ValueError('This property can\'t be accessed. Use authenticate instead.')

    @password.setter
    def password(self, password: str) -> None:
        password_hash: bytes = hashpw(password.encode('utf-8'), gensalt())
        self._password = password_hash.decode('utf-8')

    def authenticate(self, password: str) -> bool:
        return checkpw(password.encode('utf-8'), self._password.encode('utf-8'))
