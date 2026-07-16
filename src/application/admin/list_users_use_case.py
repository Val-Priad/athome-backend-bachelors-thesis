from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from domain.user.services.authorization import AuthorizationService
from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from schemas.admin_schemas.admin_users_schemas.admin_users_requests import (
    UsersListRequest,
)
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UsersListItem,
    UsersListResponse,
)


class ListUsersUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        user_repository: UserRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._transactions = transactions
        self._user_repository = user_repository
        self._authorization_service = authorization_service

    def execute(
        self, requester_id: UUID, query: UsersListRequest
    ) -> UsersListResponse:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            users, total = self._user_repository.list_users(session, query)

            return UsersListResponse(
                items=[UsersListItem.from_model(user) for user in users],
                total=total,
                page=query.page,
                page_size=query.page_size,
            )
