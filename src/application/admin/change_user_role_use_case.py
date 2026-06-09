from uuid import UUID

from domain.admin.services.admin_users_service import AdminUsersService
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from security.authorization import AuthorizationService


class ChangeUserRoleUseCase:
    def __init__(
        self,
        admin_users_service: AdminUsersService,
        authorization_service: AuthorizationService,
    ):
        self.admin_users_service = admin_users_service
        self.authorization_service = authorization_service

    def execute(
        self, requester_id: UUID, user_id: UUID, new_role: UserRole
    ) -> None:
        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self.admin_users_service.change_user_role(
                session, user_id, new_role
            )
