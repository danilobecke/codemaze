from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from repository.base import Base

class ManagerDTO(Base):
    __tablename__ = 'manager'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
