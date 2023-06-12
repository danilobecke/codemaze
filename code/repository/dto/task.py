from repository.base import Base
from sqlalchemy import Column, Integer, Sequence, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class TaskDTO(Base):
    __tablename__ = 'task'

    id = Column(Integer, Sequence('sq_task_pk'), primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    max_attempts = Column(Integer, nullable=True)
    starts_on = Column(DateTime(timezone=True), nullable=False)
    ends_on = Column(DateTime(timezone=True), nullable=True)
    file_path = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('group.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    test_cases = relationship('TestCaseDTO')
    results = relationship('ResultDTO')