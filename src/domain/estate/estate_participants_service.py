from uuid import UUID

from sqlalchemy.orm import Session

from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from exceptions.custom_exceptions.user_exceptions import (
    AgentNotFoundError,
    UserNotFoundError,
)
from schemas.estate_schemas.estate_create_request import EstateCreateRequest


class EstateParticipantsService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def check_participants(self, session: Session, data: EstateCreateRequest):
        self._check_seller(session, data.seller_id)
        self._check_broker(session, data.broker_id)

    def _check_seller(self, session: Session, seller_id: UUID | None):
        if seller_id is None:
            return

        seller = self.user_repository.get_user_by_id(session, seller_id)
        if seller.role != UserRole.user:
            raise UserNotFoundError()

    def _check_broker(self, session: Session, broker_id: UUID | None):
        if broker_id is None:
            return

        broker = self.user_repository.get_user_by_id(session, broker_id)
        if broker.role != UserRole.agent:
            raise AgentNotFoundError()
