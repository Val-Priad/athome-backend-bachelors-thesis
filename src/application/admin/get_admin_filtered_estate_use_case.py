from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from schemas.estate_schemas.responses.estate_filter_response import (
    EstateFilterResponse,
)
from security.authorization import AuthorizationService


class GetAdminFilteredEstateUseCase:
    def __init__(
        self,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
    ) -> None:
        self.estate_service = estate_service
        self.authorization_service = authorization_service

    def execute(self, filters, requester_id) -> EstateFilterResponse:
        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            return self.estate_service.get_admin_filtered_estate(
                session, filters, requester_id
            )
