from repository.dto.user import UserDTO
from sqlalchemy import Column, Integer, ForeignKey

class StudentDTO(UserDTO):
    __tablename__ = "student"
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'student'
    }