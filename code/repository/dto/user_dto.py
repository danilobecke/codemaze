from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy_utils import force_auto_coercion, PasswordType

from repository.base import Base
from repository.dto.base_dto import BaseDTO

force_auto_coercion()

class UserDTO(Base, BaseDTO):
    __tablename__ = 'user'

    id = Column(Integer, Sequence('sq_user_pk'), primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(PasswordType(schemes=[ 'pbkdf2_sha512' ]), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }
