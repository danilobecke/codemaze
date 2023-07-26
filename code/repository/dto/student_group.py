from sqlalchemy import Table, Column, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.sql import func

from repository.base import Base

# pylint: disable=not-callable
student_group = Table(
    'student_group',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('group.id'), primary_key=True),
    Column('approved', Boolean, nullable=False, default=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now())
)
