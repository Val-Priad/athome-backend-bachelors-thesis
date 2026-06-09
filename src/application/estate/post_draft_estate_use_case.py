from uuid import UUID

from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from schemas.estate_schemas.draft_request import EstateDraftRequest
from security.authorization import AuthorizationService


class PostDraftEstateUseCase:
    def __init__(self, estate_service: EstateService, authorization_service: AuthorizationService):
        self.estate_service = estate_service
        self.authorization_service = authorization_service

    def execute(
        self,
        data: EstateDraftRequest,
        requester_id: UUID,
    ) -> None:
        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self.estate_service.create_draft(
                session,
                data,
            )
