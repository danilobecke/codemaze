from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

# pylint: disable=not-callable
class BaseDTO:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
