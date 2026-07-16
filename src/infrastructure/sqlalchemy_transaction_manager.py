from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from application.ports.transaction_manager import SessionFactory


class SqlAlchemyTransactionManager:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self._session_factory()

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
