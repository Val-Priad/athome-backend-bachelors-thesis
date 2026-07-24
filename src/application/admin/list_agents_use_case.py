from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from application.users.mapping.user_response_mapper import UserResponseMapper
from domain.user.services.authorization import AuthorizationService
from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from schemas.admin_schemas.admin_users_schemas.admin_agent_response import (
    AgentListResponse,
    AgentsListItem,
)
from schemas.admin_schemas.admin_users_schemas.admin_agents_request import (
    AgentListRequest,
)


class ListAgentsUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        user_repository: UserRepository,
        authorization_service: AuthorizationService,
        response_mapper: UserResponseMapper,
    ) -> None:
        self._transactions = transactions
        self._user_repository = user_repository
        self._authorization_service = authorization_service
        self._response_mapper = response_mapper

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
                    self._response_mapper.to_response(AgentsListItem, row)
                    for row in agents
                ],
                total=total,
                page=query.page,
                page_size=query.page_size,
            )
