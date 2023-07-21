from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from repository.dto.student_group import student_group
from repository.dto.user_dto import UserDTO
if TYPE_CHECKING:
    from repository.dto.group_dto import GroupDTO

class StudentDTO(UserDTO):
    __tablename__ = 'student'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    groups = relationship('GroupDTO', secondary=student_group, back_populates='students')

    __mapper_args__ = {
        'polymorphic_identity':'student'
    }
