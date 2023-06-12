from sqlalchemy import Table, Column, ForeignKey, Integer, Boolean
from repository.base import Base

student_group = Table(
    'student_group',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('group.id'), primary_key=True),
    Column('approved', Boolean, nullable=False, default=False)
)