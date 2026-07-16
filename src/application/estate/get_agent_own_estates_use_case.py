from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from schemas.estate_schemas.requests.estate_filter_request import (
    EstateAdminFilterRequest,
    EstateAgentOwnFilterRequest,
)
from security.authorization import AuthorizationService


class GetAgentOwnEstatesUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
    ) -> None:
        self._transactions = transactions
        self._estate_service = estate_service
        self._authorization_service = authorization_service

    def execute(
        self,
        requester_id: UUID,
        filters: EstateAgentOwnFilterRequest,
    ):

        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.agent
            )

            admin_filters = EstateAdminFilterRequest(
                **filters.model_dump(),
                agent_id=requester_id,
                seller_id=None,
            )

            return self._estate_service.get_admin_filtered_estate(
                session,
                admin_filters,
                requester_id,
            )
