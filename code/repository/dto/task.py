from sqlalchemy import Column, Integer, Sequence, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from repository.base import Base
from repository.dto.base_dto import BaseDTO

# pylint: disable=not-callable
class TaskDTO(Base, BaseDTO):
    __tablename__ = 'task'

    id = Column(Integer, Sequence('sq_task_pk'), primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    max_attempts = Column(Integer, nullable=True)
    starts_on = Column(DateTime(timezone=True), server_default=func.now())
    ends_on = Column(DateTime(timezone=True), nullable=True)
    file_path = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('group.id'), nullable=False)
