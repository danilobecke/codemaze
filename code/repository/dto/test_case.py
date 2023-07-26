from sqlalchemy import Column, Integer, Sequence, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func

from repository.base import Base

# pylint: disable=not-callable
class TestCaseDTO(Base):
    __tablename__ = 'test_case'

    id = Column(Integer, Sequence('sq_test_case_pk'), primary_key=True, autoincrement=True)
    input_file_path = Column(String, nullable=False)
    output_file_path = Column(String, nullable=False)
    closed = Column(Boolean, nullable=False)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
