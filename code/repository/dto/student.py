from sqlalchemy import Column, Integer, ForeignKey

from repository.dto.user_dto import UserDTO

# pylint: disable=too-few-public-methods
class StudentDTO(UserDTO):
    __tablename__ = 'student'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'student'
    }
