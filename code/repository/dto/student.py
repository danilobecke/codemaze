from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from repository.dto.user_dto import UserDTO

class StudentDTO(UserDTO):
    __tablename__ = 'student'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'student'
    }
