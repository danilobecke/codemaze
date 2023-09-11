from sqlalchemy import Integer, Sequence, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from repository.base import Base

class ResultDTO(Base):
    __tablename__ = 'result'

    id: Mapped[int] = mapped_column(Integer, Sequence('sq_result_pk'), primary_key=True, autoincrement=True)
    correct_open: Mapped[int]
    correct_closed: Mapped[int]
    file_path: Mapped[str]
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('task.id'), nullable=False)
