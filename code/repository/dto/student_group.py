from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from repository.base import Base

class StudentGroupDTO(Base):
    __tablename__ = 'student_group'
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('group.id'), nullable=False, primary_key=True)
    approved: Mapped[bool]
