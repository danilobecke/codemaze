from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Sequence, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import func

from repository.base import Base

# pylint: disable=not-callable
class TaskDTO(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(Integer, Sequence('sq_task_pk'), primary_key=True, autoincrement=True)
    name: Mapped[str]
    max_attempts: Mapped[Optional[int]]
    starts_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ends_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    languages: Mapped[list[str]] = mapped_column(ARRAY(String))
    file_path: Mapped[str]
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('group.id'), nullable=False)
