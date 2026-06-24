from uuid import UUID

from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from schemas.estate_schemas.requests.estate_filter_request import (
    EstateAdminFilterRequest,
    EstateAgentOwnFilterRequest,
)
from security.authorization import AuthorizationService


class GetAgentOwnEstatesUseCase:
    def __init__(
        self,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
    ) -> None:
        self.estate_service = estate_service
        self.authorization_service = authorization_service

    def execute(
        self,
        requester_id: UUID,
        filters: EstateAgentOwnFilterRequest,
    ):

        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.agent
            )

            admin_filters = EstateAdminFilterRequest(
                **filters.model_dump(),
                agent_id=requester_id,
                seller_id=None,
            )

            return self.estate_service.get_admin_filtered_estate(
                session,
                admin_filters,
                requester_id,
            )
