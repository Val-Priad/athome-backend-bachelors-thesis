from uuid import UUID

from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
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
        user_repository: UserRepository,
        authorization_service: AuthorizationService,
    ):
        self.user_repository = user_repository
        self.authorization_service = authorization_service

    def execute(
        self, requester_id: UUID, query: UsersListRequest
    ) -> UsersListResponse:
        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            users, total = self.user_repository.list_users(session, query)

            return UsersListResponse(
                items=[UsersListItem.from_model(user) for user in users],
                total=total,
                page=query.page,
                page_size=query.page_size,
            )
