from uuid import UUID

from domain.admin.services.admin_users_service import AdminUsersService
from domain.user.user_model import UserRole
from infrastructure.db import db_session


class ChangeUserRoleUseCase:
    def __init__(self, admin_users_service: AdminUsersService):
        self.admin_users_service = admin_users_service

    def execute(self, requester_id: UUID, user_id: UUID, new_role: UserRole) -> None:
        with db_session() as session:
            self.admin_users_service.change_user_role(
                session, requester_id, user_id, new_role
            )
