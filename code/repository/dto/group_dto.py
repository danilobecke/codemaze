from sqlalchemy import Column, Integer, Sequence, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func

from repository.base import Base

# pylint: disable=too-few-public-methods,not-callable
class GroupDTO(Base):
    __tablename__ = 'group'

    id = Column(Integer, Sequence('sq_group_pk'), primary_key=True, autoincrement=True)
    active = Column(Boolean, nullable=False, default=True)
    name = Column(String, nullable=False)
    code = Column(String(6), nullable=False, unique=True)
    manager_id = Column(Integer, ForeignKey('manager.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
