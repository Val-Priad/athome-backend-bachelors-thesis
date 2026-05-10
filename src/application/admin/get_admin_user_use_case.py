from uuid import UUID

from domain.admin.services.admin_users_service import AdminUsersService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UserResponse,
)


class GetAdminUserUseCase:
    def __init__(self, admin_users_service: AdminUsersService):
        self.admin_users_service = admin_users_service

    def execute(self, requester_id: UUID, user_id: UUID) -> UserResponse:
        with db_session() as db:
            self.admin_users_service.ensure_has_rights(db, requester_id, UserRole.admin)
            user = self.admin_users_service.get_user_by_id(db, user_id)
            return UserResponse.from_model(user)
