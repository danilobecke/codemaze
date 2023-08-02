from sqlalchemy import Column, Integer, Sequence, String, ForeignKey, Boolean

from repository.base import Base
from repository.dto.base_dto import BaseDTO

class GroupDTO(Base, BaseDTO):
    __tablename__ = 'group'

    id = Column(Integer, Sequence('sq_group_pk'), primary_key=True, autoincrement=True)
    active = Column(Boolean, nullable=False, default=True)
    name = Column(String, nullable=False)
    code = Column(String(6), nullable=False, unique=True)
    manager_id = Column(Integer, ForeignKey('manager.id'), nullable=False)
