from typing import TypeVar, Generic

from sqlalchemy.exc import IntegrityError

from helpers.exceptions import Internal_UniqueViolation, ServerError, NotFound
from helpers.unwrapper import unwrap
from repository.base import Base
from repository.database import Database

M = TypeVar('M', bound=Base)

class AbstractRepository(Generic[M]):
    def __init__(self, klass) -> None:
        self.__class = klass
        self._session = unwrap(Database.shared).session

    def find_all(self) -> list[M]:
        return self._session.query(self.__class).all()

    def find(self, id: int) -> M:
        model = self._session.query(self.__class).get(id)
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
