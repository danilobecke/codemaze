from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.sql import func

# pylint: disable=not-callable
class Base(DeclarativeBase):
    id: Mapped[int]
    created_at = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())
