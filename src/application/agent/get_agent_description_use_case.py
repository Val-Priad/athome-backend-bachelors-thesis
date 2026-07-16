from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.user.services.agent_service import AgentService
from schemas.agent_schemas.agent_responses import AgentDescriptionResponse


class GetAgentDescriptionUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        agent_service: AgentService,
    ) -> None:
        self._transactions = transactions
        self._agent_service = agent_service

    def execute(self, agent_id: UUID) -> AgentDescriptionResponse:
        with self._transactions.session() as session:
            user = self._agent_service.get_agent_description(session, agent_id)
            return AgentDescriptionResponse.from_model(user)
