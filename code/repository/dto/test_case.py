from sqlalchemy import Integer, Sequence, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from repository.base import Base

class TestCaseDTO(Base):
    __tablename__ = 'test_case'

    id: Mapped[int] = mapped_column(Integer, Sequence('sq_test_case_pk'), primary_key=True, autoincrement=True)
    input_file_path: Mapped[str]
    output_file_path: Mapped[str]
    closed: Mapped[bool]
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('task.id'), nullable=False)
