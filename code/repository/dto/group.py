from repository.base import Base
from sqlalchemy import Column, Integer, Sequence, String, ForeignKey
from sqlalchemy.orm import relationship

class GroupDTO(Base):
    __tablename__ = "group"

    id = Column(Integer, Sequence('sq_group_pk'), primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String(6), nullable=False)
    manager_id = Column(Integer, ForeignKey('manager.id'), nullable=False)
    manager = relationship('ManagerDTO', back_populates='groups')