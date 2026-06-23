from uuid import UUID

from domain.estate.estate_participants_service import EstateParticipantsService
from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from schemas.estate_schemas.requests.estate_update_request import (
    EstateUpdateRequest,
)
from schemas.estate_schemas.responses.estate_create_response import (
    EstateIDResponse,
)
from security.authorization import AuthorizationService


class UpdateEstateUseCase:
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
        estate_id: UUID,
        data: EstateUpdateRequest,
        requester_id: UUID,
    ) -> EstateIDResponse:
        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self.participants_service.check_participants(session, data)
            estate = self.estate_service.update_estate(
                session=session,
                estate_id=estate_id,
                data=data,
            )

            return EstateIDResponse.from_model(estate)
