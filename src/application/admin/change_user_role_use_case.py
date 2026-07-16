from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.admin.services.admin_users_service import AdminUsersService
from domain.user.user_model import UserRole
from security.authorization import AuthorizationService


class ChangeUserRoleUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        admin_users_service: AdminUsersService,
        authorization_service: AuthorizationService,
    ) -> None:
        self._transactions = transactions
        self._admin_users_service = admin_users_service
        self._authorization_service = authorization_service

    def execute(
        self, requester_id: UUID, user_id: UUID, new_role: UserRole
    ) -> None:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self._admin_users_service.change_user_role(
                session, user_id, new_role
            )
