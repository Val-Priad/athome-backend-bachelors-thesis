from uuid import UUID

from domain.user.services.agent_service import AgentService
from infrastructure.db import db_session
from schemas.agent_schemas.agent_responses import AgentDescriptionResponse


class GetAgentDescriptionUseCase:
    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service

    def execute(self, agent_id: UUID) -> AgentDescriptionResponse:
        with db_session() as session:
            user = self.agent_service.get_agent_description(session, agent_id)
            return AgentDescriptionResponse.from_model(user)
