# pylint: disable=unused-import

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.base import Engine

from repository.base import Base
import repository.table_builder # must be imported to initialize the database

class Database:
    shared: Database | None = None

    def __init__(self, db_string: str) -> None:
        connection = self.__create_connection(db_string)
        self.session = sessionmaker(bind=connection)()

    def __create_connection(self, db_string: str) -> Engine:
        connection = create_engine(db_string)
        Base.metadata.create_all(connection)
        return connection

    @staticmethod
    def initialize(db_string: str) -> None:
        if Database.shared is not None:
            return
        Database.shared = Database(db_string)
