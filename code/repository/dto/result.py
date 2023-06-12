from repository.base import Base
from sqlalchemy import Column, Integer, Sequence, String, ForeignKey

class ResultDTO(Base):
    __tablename__ = 'result'

    id = Column(Integer, Sequence('sq_result_pk'), primary_key=True, autoincrement=True)
    correct_open = Column(Integer, nullable=False)
    correct_closed = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)