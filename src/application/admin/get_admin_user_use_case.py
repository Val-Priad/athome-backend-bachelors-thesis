from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from application.users.mapping.user_response_mapper import UserResponseMapper
from domain.user.services.authorization import AuthorizationService
from domain.user.user_model import UserRole
from domain.user.user_repository import UserRepository
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UserResponse,
)


class GetAdminUserUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        authorization_service: AuthorizationService,
        user_repository: UserRepository,
        response_mapper: UserResponseMapper,
    ) -> None:
        self._transactions = transactions
        self._authorization_service = authorization_service
        self._user_repository = user_repository
        self._response_mapper = response_mapper

    def execute(self, requester_id: UUID, user_id: UUID) -> UserResponse:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            user = self._user_repository.get_user_by_id(session, user_id)
            return self._response_mapper.to_response(UserResponse, user)
