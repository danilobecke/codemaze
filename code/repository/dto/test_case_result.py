from typing import Optional

from sqlalchemy import Integer, Sequence, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from repository.base import Base

class TestCaseResultDTO(Base):
    __tablename__ = 'test_case_result'

    id: Mapped[int] = mapped_column(Integer, Sequence('sq_test_case_pk'), primary_key=True, autoincrement=True)
    test_case_id: Mapped[int] = mapped_column(Integer, ForeignKey('test_case.id'), nullable=False)
    success: Mapped[bool]
    diff: Mapped[Optional[str]]
