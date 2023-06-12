from repository.dto.user import UserDTO
from sqlalchemy import Column, Integer, ForeignKey

class ManagerDTO(UserDTO):
    __tablename__ = "manager"
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'manager'
    }