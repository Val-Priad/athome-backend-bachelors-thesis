from uuid import UUID

from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from exceptions.custom_exceptions.user_exceptions import AgentNotFoundError
from infrastructure.db import db_session
from schemas.estate_schemas.create_request import EstateCreateRequest
from security.authorization import AuthorizationService


class CreateEstateUseCase:
    def __init__(
        self,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
    ):
        self.estate_service = estate_service
        self.authorization_service = authorization_service

    def execute(
        self,
        data: EstateCreateRequest,
        requester_id: UUID,
    ) -> None:
        with db_session() as session:
            requester = (
                self.authorization_service.user_repository.get_user_by_id(
                    session, requester_id
                )
            )
            if data.broker_id is None:
                raise AgentNotFoundError()

            broker = self.authorization_service.user_repository.get_user_by_id(
                session, data.broker_id
            )
            if broker.role != UserRole.agent:
                raise AgentNotFoundError()

            self.estate_service.create_estate(
                session,
                data,
                requester.role,
            )
