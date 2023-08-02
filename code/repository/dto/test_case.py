from sqlalchemy import Column, Integer, Sequence, String, Boolean, ForeignKey

from repository.base import Base
from repository.dto.base_dto import BaseDTO

class TestCaseDTO(Base, BaseDTO):
    __tablename__ = 'test_case'

    id = Column(Integer, Sequence('sq_test_case_pk'), primary_key=True, autoincrement=True)
    input_file_path = Column(String, nullable=False)
    output_file_path = Column(String, nullable=False)
    closed = Column(Boolean, nullable=False)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
