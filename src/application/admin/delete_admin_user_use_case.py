from uuid import UUID

from domain.admin.services.admin_users_service import AdminUsersService
from infrastructure.db import db_session


class DeleteAdminUserUseCase:
    def __init__(self, admin_users_service: AdminUsersService):
        self.admin_users_service = admin_users_service

    def execute(self, requester_id: UUID, user_id: UUID) -> None:
        with db_session() as session:
            self.admin_users_service.delete_user(session, requester_id, user_id)
