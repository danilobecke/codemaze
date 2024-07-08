# pylint: disable=unused-import

from __future__ import annotations

from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.base import Engine

from helpers.unwrapper import unwrap
from repository.base import Base
import repository.table_builder # must be imported to initialize the database

class Database:
    shared: Database | None = None

    @property
    def session(self) -> Session | None:
        try:
            return g.session # type: ignore
        except AttributeError:
            return None

    def __init__(self, db_string: str, app: Flask) -> None:
        engine = self.__create_engine(db_string)
        self.session_maker = sessionmaker(bind=engine)
        app.before_request(Database.__create_session)
        app.teardown_request(Database.close_session)

    def __create_engine(self, db_string: str) -> Engine:
        engine = create_engine(db_string)
        Base.metadata.create_all(engine)
        return engine

    @staticmethod
    def initialize(db_string: str, app: Flask) -> None:
        if Database.shared is not None:
            return
        Database.shared = Database(db_string, app)

    @staticmethod
    def __create_session() -> None:
        g.session = unwrap(Database.shared).session_maker()

    # pylint: disable=unused-argument
    @staticmethod
    def close_session(exception: BaseException | None = None) -> None:
        session: Session | None = g.pop('session', None)
        if session:
            session.close()
