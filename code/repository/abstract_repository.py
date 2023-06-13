from repository.database import Database
from repository.base import Base
from typing import TypeVar, Generic
from helpers.exceptions import *

M = TypeVar('M', bound=Base)

class AbstractRepository(Generic[M]):
    def __init__(self, klass):
        self.__class = klass
        self.__session = Database.shared.session

    def find_all(self) -> list[M]:
        return self.__session.query(self.__class).all()

    def find(self, id: int) -> M:
        if id < 1:
             raise InvalidID()
        model = self.__session.query(self.__class).get(id)
        if model is None:
            raise NotFound()
        return model

    def add(self, model: M):
        self.__session.add(model)
        self.__session.commit()

    def delete(self, id: int):
        obj = self.find(id)
        self.__session.delete(obj)
        self.__session.commit()