from uuid import UUID

from sqlalchemy.orm import Session

from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from exceptions.custom_exceptions.user_exceptions import (
    AgentNotFoundError,
    UserNotFoundError,
)


class AgentService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_agent_description(self, session: Session, agent_id: UUID):
        try:
            user = self.user_repository.get_user_by_id(session, agent_id)
        except UserNotFoundError:
            raise AgentNotFoundError()
        if user.role != UserRole.agent:
            raise AgentNotFoundError()
        return user
