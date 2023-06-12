from repository.dto.user import UserDTO
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class ManagerDTO(UserDTO):
    __tablename__ = 'manager'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    groups = relationship('GroupDTO', back_populates='manager', cascade='all, delete')

    __mapper_args__ = {
        'polymorphic_identity':'manager'
    }