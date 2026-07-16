from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from domain.user.user_repository import UserRepository


class DeleteMeUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        user_repository: UserRepository,
    ) -> None:
        self._transactions = transactions
        self._user_repository = user_repository

    def execute(self, user_id: UUID) -> None:
        with self._transactions.session() as session:
            session.delete(
                self._user_repository.get_user_by_id(session, user_id)
            )
