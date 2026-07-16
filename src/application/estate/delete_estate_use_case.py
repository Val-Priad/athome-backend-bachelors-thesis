from application.transactions import TransactionManagerProtocol
from domain.estate.estate_repository import EstateRepository
from domain.user.user_model import UserRole
from security.authorization import AuthorizationService


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

    def execute(self, estate_id, requester_id):
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self._estate_repository.delete_estate_by_id(session, estate_id)
