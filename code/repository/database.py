from typing import Self
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from repository.base import Base
import repository.table_builder

class Database:
    shared: Self | None = None

    def __init__(self, db_string: str):
        connection = self.__create_connection(db_string)
        self.session = sessionmaker(bind=connection)()
    
    def __create_connection(self, db_string: str):
        connection = create_engine(db_string)
        Base.metadata.create_all(connection)
        return connection

    @staticmethod
    def initialize(db_string: str):
        if Database.shared is not None:
            return
        Database.shared = Database(db_string)