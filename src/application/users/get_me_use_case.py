from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from application.users.mapping.user_response_mapper import UserResponseMapper
from domain.user.user_repository import UserRepository
from schemas.me_schemas.me_responses import MeResponse


class GetMeUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        user_repository: UserRepository,
        response_mapper: UserResponseMapper,
    ) -> None:
        self._transactions = transactions
        self._user_repository = user_repository
        self._response_mapper = response_mapper

    def execute(self, user_id: UUID) -> MeResponse:
        with self._transactions.session() as session:
            user = self._user_repository.get_user_by_id(session, user_id)
            return self._response_mapper.to_response(MeResponse, user)
