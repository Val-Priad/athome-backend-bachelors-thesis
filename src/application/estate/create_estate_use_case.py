from uuid import UUID

from domain.estate.estate_participants_service import EstateParticipantsService
from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from schemas.estate_schemas.estate_create_request import EstateCreateRequest
from schemas.estate_schemas.estate_create_response import EstateCreateResponse
from security.authorization import AuthorizationService


class CreateEstateUseCase:
    def __init__(
        self,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
        participants_service: EstateParticipantsService,
    ):
        self.estate_service = estate_service
        self.authorization_service = authorization_service
        self.participants_service = participants_service

    def execute(
        self,
        data: EstateCreateRequest,
        requester_id: UUID,
    ) -> EstateCreateResponse:

        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self.participants_service.check_participants(session, data)

        vicinities = self.estate_service.get_vicinities_or_empty(data.location)

        with db_session() as session:
            estate = self.estate_service.create_estate(
                session, data, vicinities
            )
            return EstateCreateResponse(id=estate.id)
