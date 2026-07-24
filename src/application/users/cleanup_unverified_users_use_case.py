import logging
from datetime import datetime, timedelta, timezone

from application.ports.transaction_manager import TransactionManagerProtocol
from domain.user.user_repository import UserRepository

_logger = logging.getLogger(__name__)

MAX_UNVERIFIED_AGE = timedelta(hours=24)


class CleanupUnverifiedUsersUseCase:
    def __init__(
        self,
        *,
        transactions: TransactionManagerProtocol,
        user_repository: UserRepository,
    ) -> None:
        self._transactions = transactions
        self._user_repository = user_repository

    def execute(self) -> int:
        cutoff = datetime.now(timezone.utc) - MAX_UNVERIFIED_AGE

        with self._transactions.session() as session:
            deleted = self._user_repository.delete_unverified_created_before(
                session=session,
                cutoff=cutoff,
            )

        _logger.info("Deleted %s expired unverified users", deleted)
        return deleted
