from sqlalchemy import Integer, Sequence, String, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, Mapped

from repository.base import Base

class GroupDTO(Base):
    __tablename__ = 'group'

    id: Mapped[int] = mapped_column(Integer, Sequence('sq_group_pk'), primary_key=True, autoincrement=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    name: Mapped[str]
    code: Mapped[str] = mapped_column(String(6), nullable=False, unique=True)
    manager_id: Mapped[int] = mapped_column(Integer, ForeignKey('manager.id'), nullable=False)
