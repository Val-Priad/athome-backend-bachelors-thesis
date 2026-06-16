from uuid import UUID

from domain.estate.estate_participants_service import EstateParticipantsService
from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from schemas.estate_schemas.estate_create_request import EstateCreateRequest
from schemas.estate_schemas.estate_create_response import EstateIDResponse
from schemas.estate_schemas.estate_create_type import EstateCreateType
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
    ) -> EstateIDResponse:
        creation_data = EstateCreateType(**data.model_dump())

        with db_session() as session:
            self._ensure_rights_and_data_validity(session, requester_id, data)

        vicinities = self.estate_service.get_vicinities_or_empty(data.location)

        with db_session() as session:
            self._ensure_rights_and_data_validity(session, requester_id, data)
            estate = self.estate_service.create_estate(
                session, creation_data, vicinities
            )
            return EstateIDResponse(id=estate.id)

    def _ensure_rights_and_data_validity(self, session, requester_id, data):
        self.authorization_service.ensure_has_rights(
            session, requester_id, UserRole.admin
        )
        self.participants_service.check_participants(session, data)
