from uuid import UUID

from domain.admin.services.admin_users_service import AdminUsersService
from infrastructure.db import db_session
from schemas.admin_schemas.admin_users_schemas.admin_users_requests import (
    UsersListRequest,
)
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UsersListItem,
    UsersListResponse,
)


class ListUsersUseCase:
    def __init__(self, admin_users_service: AdminUsersService):
        self.admin_users_service = admin_users_service

    def execute(
        self, requester_id: UUID, query: UsersListRequest
    ) -> UsersListResponse:
        with db_session() as session:
            users, total = self.admin_users_service.list_users(
                session,
                requester_id,
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
