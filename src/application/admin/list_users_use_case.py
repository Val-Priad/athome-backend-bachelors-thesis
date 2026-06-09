from uuid import UUID

from domain.admin.services.admin_users_service import AdminUsersService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from schemas.admin_schemas.admin_users_schemas.admin_users_requests import (
    UsersListRequest,
)
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UsersListItem,
    UsersListResponse,
)
from security.authorization import AuthorizationService


class ListUsersUseCase:
    def __init__(
        self,
        admin_users_service: AdminUsersService,
        authorization_service: AuthorizationService,
    ):
        self.admin_users_service = admin_users_service
        self.authorization_service = authorization_service

    def execute(
        self, requester_id: UUID, query: UsersListRequest
    ) -> UsersListResponse:
        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            users, total = self.admin_users_service.list_users(
                session,
                role=None,
                email=query.email,
                name=query.name,
                phone_number=query.phone_number,
                is_email_verified=query.is_email_verified,
                sort_by=query.sort_by,
                sort_order=query.sort_order,
                page=query.page,
                page_size=query.page_size,
            )

            return UsersListResponse(
                items=[UsersListItem.from_model(user) for user in users],
                total=total,
                page=query.page,
                page_size=query.page_size,
            )
