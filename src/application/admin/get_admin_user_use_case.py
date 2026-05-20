from uuid import UUID

from domain.admin.services.admin_users_service import AdminUsersService
from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from infrastructure.db import db_session
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UserResponse,
)
from security.authorization import AuthorizationService


class GetAdminUserUseCase:
    def __init__(
        self,
        admin_users_service: AdminUsersService,
        authorization_service: AuthorizationService,
        user_repository: UserRepository,
    ):
        self.admin_users_service = admin_users_service
        self.authorization_service = authorization_service
        self.user_repository = user_repository

    def execute(self, requester_id: UUID, user_id: UUID) -> UserResponse:
        with db_session() as db:
            self.authorization_service.ensure_has_rights(
                db, requester_id, UserRole.admin
            )
            user = self.user_repository.get_user_by_id(db, user_id)
            return UserResponse.from_model(user)
