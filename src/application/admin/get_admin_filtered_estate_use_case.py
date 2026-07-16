from application.transactions import TransactionManagerProtocol
from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from schemas.estate_schemas.responses.estate_filter_response import (
    EstateFilterResponse,
)
from security.authorization import AuthorizationService


class GetAdminFilteredEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
    ) -> None:
        self._transactions = transactions
        self._estate_service = estate_service
        self._authorization_service = authorization_service

    def execute(self, filters, requester_id) -> EstateFilterResponse:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            return self._estate_service.get_admin_filtered_estate(
                session, filters, requester_id
            )
