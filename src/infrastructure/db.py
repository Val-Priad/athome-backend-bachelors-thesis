from contextlib import contextmanager

from flask import Flask
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


_engine: Engine | None = None
_SessionFactory: sessionmaker | None = None


def init_db(app: Flask) -> None:
    global _engine, _SessionFactory

    database_url = app.config["DATABASE_URL"]

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    if _engine is not None:
        _engine.dispose()

    _engine = create_db_engine(database_url)
    _SessionFactory = create_session_factory(_engine)


def create_db_engine(database_url: str):
    return create_engine(database_url)


def create_session_factory(engine: Engine):
    return sessionmaker(
        bind=engine,
    )


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("Database engine is not initialized")

    return _engine


def get_session() -> Session:
    if _SessionFactory is None:
        raise RuntimeError("Database session factory is not initialized")
    return _SessionFactory()


@contextmanager
def db_session():
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
