from sqlalchemy import Integer, Sequence, String
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy_utils import force_auto_coercion, PasswordType

from repository.base import Base

force_auto_coercion()

class UserDTO(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, Sequence('sq_user_pk'), primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password = mapped_column(PasswordType(schemes=[ 'pbkdf2_sha512' ]), nullable=False)
    name: Mapped[str]
    type: Mapped[str]

    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':'type'
    }
