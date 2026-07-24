from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from application.users.mapping.user_response_mapper import UserResponseMapper
from domain.user.services.agent_service import AgentService
from schemas.agent_schemas.agent_responses import AgentDescriptionResponse


class GetAgentDescriptionUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        agent_service: AgentService,
        response_mapper: UserResponseMapper,
    ) -> None:
        self._transactions = transactions
        self._agent_service = agent_service
        self._response_mapper = response_mapper

    def execute(self, agent_id: UUID) -> AgentDescriptionResponse:
        with self._transactions.session() as session:
            user = self._agent_service.get_agent_description(session, agent_id)
            return self._response_mapper.to_response(
                AgentDescriptionResponse, user
            )
