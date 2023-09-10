from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from repository.dto.user_dto import UserDTO

class ManagerDTO(UserDTO):
    __tablename__ = 'manager'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'manager'
    }
