from dataclasses import dataclass

from flask import Flask
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


@dataclass(frozen=True, slots=True)
class DatabaseState:
    engine: Engine
    session_factory: sessionmaker[Session]


class Database:
    extension_key = "database"

    def init_app(self, app: Flask) -> None:
        database_url = app.config["DATABASE_URL"]

        if not database_url:
            raise RuntimeError("DATABASE_URL is not set")

        engine = create_db_engine(database_url)
        session_factory = create_session_factory(engine)

        app.extensions[self.extension_key] = DatabaseState(
            engine=engine,
            session_factory=session_factory,
        )

    def get_state(self, app: Flask) -> DatabaseState:
        state = app.extensions.get(self.extension_key)

        if not isinstance(state, DatabaseState):
            raise RuntimeError("Database is not initialized for this app")

        return state

    def get_engine(self, app: Flask) -> Engine:
        return self.get_state(app).engine

    def get_session_factory(self, app: Flask) -> sessionmaker[Session]:
        return self.get_state(app).session_factory


def create_db_engine(database_url: str) -> Engine:
    return create_engine(database_url)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
    )


db = Database()
