from sqlalchemy import Column, Integer, ForeignKey

from repository.dto.user_dto import UserDTO

# pylint: disable=too-few-public-methods
class ManagerDTO(UserDTO):
    __tablename__ = 'manager'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'manager'
    }
