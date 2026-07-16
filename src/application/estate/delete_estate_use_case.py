from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from domain.estate.estate_repository import EstateRepository
from domain.user.services.authorization import AuthorizationService
from domain.user.user_model import UserRole


class DeleteEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_repository: EstateRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._transactions = transactions
        self._estate_repository = estate_repository
        self._authorization_service = authorization_service

    def execute(self, estate_id: UUID, requester_id: UUID) -> None:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self._estate_repository.delete_estate_by_id(session, estate_id)
