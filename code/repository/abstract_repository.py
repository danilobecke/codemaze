from repository.database import Database
from repository.base import Base
from typing import TypeVar, Generic
from helpers.exceptions import *
from psycopg2.errors import UniqueViolation

M = TypeVar('M', bound=Base)

class AbstractRepository(Generic[M]):
    def __init__(self, klass):
        self.__class = klass
        self._session = Database.shared.session

    def find_all(self) -> list[M]:
        return self._session.query(self.__class).all()

    def find(self, id: int) -> M:
        model = self._session.query(self.__class).get(id)
        if model is None:
            raise NotFound()
        return model

    def add(self, model: M, raise_unique_violation_error: bool = False):
        try:
            self._session.add(model)
            self._session.commit()
            return model
        except UniqueViolation:
            self._session.rollback()
            raise Internal_UniqueViolation() if raise_unique_violation_error else ServerError()
        except Exception as e:
            self._session.rollback()
            raise ServerError()

    def delete(self, id: int):
        obj = self.find(id)
        try:
            self._session.delete(obj)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ServerError()

    def update_session(self):
        try:
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ServerError()
