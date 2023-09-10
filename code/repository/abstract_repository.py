from typing import TypeVar, Generic

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from helpers.exceptions import Internal_UniqueViolation, ServerError, NotFound
from helpers.unwrapper import unwrap
from repository.base import Base
from repository.database import Database

M = TypeVar('M', bound=Base)

class AbstractRepository(Generic[M]):
    def __init__(self, klass: type[M]) -> None:
        self.__class = klass
        self._session = unwrap(Database.shared).session

    def find_all(self) -> list[M]:
        stm = select(self.__class).order_by(self.__class.created_at)
        return list(self._session.scalars(stm).all())

    def find(self, id: int) -> M:
        stm = select(self.__class).where(self.__class.id == id)
        model = self._session.scalars(stm).first()
        if model is None:
            raise NotFound()
        return model

    def add(self, model: M, raise_unique_violation_error: bool = False) -> M:
        try:
            self._session.add(model)
            self._session.commit()
            return model
        except IntegrityError as e:
            self._session.rollback()
            raise Internal_UniqueViolation() if raise_unique_violation_error else ServerError() from e
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def delete(self, id: int) -> None:
        obj = self.find(id)
        try:
            self._session.delete(obj)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def update_session(self) -> None:
        try:
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e
