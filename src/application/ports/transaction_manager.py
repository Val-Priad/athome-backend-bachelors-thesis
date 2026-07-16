from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Protocol

from sqlalchemy.orm import Session

SessionFactory = Callable[[], Session]


class TransactionManagerProtocol(Protocol):
    def session(self) -> AbstractContextManager[Session]: ...
