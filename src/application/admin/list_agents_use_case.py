from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from schemas.admin_schemas.admin_users_schemas.admin_agent_response import (
    AgentListResponse,
    AgentsListItem,
)
from schemas.admin_schemas.admin_users_schemas.admin_agents_request import (
    AgentListRequest,
)
from security.authorization import AuthorizationService


class ListAgentsUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        user_repository: UserRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._transactions = transactions
        self._user_repository = user_repository
        self._authorization_service = authorization_service

    def execute(
        self, requester_id: UUID, query: AgentListRequest
    ) -> AgentListResponse:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            agents, total = self._user_repository.list_agents(session, query)

            return AgentListResponse(
                items=[
                    AgentsListItem(
                        id=row.id,
                        email=row.email,
                        name=row.name,
                        phone_number=row.phone_number,
                        avatar_key=row.avatar_key,
                        estate_qty=row.estate_qty,
                        created_at=row.created_at,
                    )
                    for row in agents
                ],
                total=total,
                page=query.page,
                page_size=query.page_size,
            )
