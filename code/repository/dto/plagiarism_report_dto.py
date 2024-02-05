from sqlalchemy import Integer, Sequence, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from repository.base import Base

class PlagiarismReportDTO(Base):
    __tablename__ = 'plagiarism_report'

    id: Mapped[int] = mapped_column(Integer, Sequence('sq_plagiarism_report_pk'), primary_key=True, autoincrement=True)
    url: Mapped[str]
    language: Mapped[str]
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('task.id'), nullable=False)
