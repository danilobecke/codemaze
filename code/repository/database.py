from typing import Self

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from repository.base import Base
import repository.table_builder

class Database:
    shared: Self | None = None

    def __init__(self, db_string: str, resetting: bool):
        connection = self.__create_connection(db_string, resetting)
        self.session = sessionmaker(bind=connection)()

    def __create_connection(self, db_string: str, resetting: bool):
        connection = create_engine(db_string)
        if resetting:
            Base.metadata.drop_all(bind=connection)
        Base.metadata.create_all(connection)
        return connection

    @staticmethod
    def initialize(db_string: str, resetting: bool = False):
        if Database.shared is not None:
            return
        Database.shared = Database(db_string, resetting)
