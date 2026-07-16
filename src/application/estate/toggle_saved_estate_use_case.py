from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.estate.estate_repository import EstateRepository
from exceptions.custom_exceptions.estate_exceptions import EstateNotFoundError


class ToggleSavedEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_repository: EstateRepository,
    ) -> None:
        self._transactions = transactions
        self._estate_repository = estate_repository

    def execute(self, requester_id: UUID, estate_id: UUID) -> None:
        with self._transactions.session() as session:
            if not self._estate_repository.estate_exists(session, estate_id):
                raise EstateNotFoundError()

            self._estate_repository.toggle_saved(
                session, requester_id, estate_id
            )
