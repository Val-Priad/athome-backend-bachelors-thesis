from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from application.transactions.transaction_manager_protocol import (
    SessionFactory,
)


class TransactionManager:
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
