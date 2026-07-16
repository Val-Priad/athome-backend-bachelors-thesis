from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.admin.services.admin_users_service import AdminUsersService
from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UserResponse,
)
from security.authorization import AuthorizationService


class GetAdminUserUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        admin_users_service: AdminUsersService,
        authorization_service: AuthorizationService,
        user_repository: UserRepository,
    ) -> None:
        self._transactions = transactions
        self._admin_users_service = admin_users_service
        self._authorization_service = authorization_service
        self._user_repository = user_repository

    def execute(self, requester_id: UUID, user_id: UUID) -> UserResponse:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            user = self._user_repository.get_user_by_id(session, user_id)
            return UserResponse.from_model(user)
