from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.user.user_repository import UserRepository
from schemas.me_schemas.me_responses import MeResponse


class GetMeUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        user_repository: UserRepository,
    ) -> None:
        self._transactions = transactions
        self._user_repository = user_repository

    def execute(self, user_id: UUID) -> MeResponse:
        with self._transactions.session() as session:
            user = self._user_repository.get_user_by_id(session, user_id)
            return MeResponse.from_model(user)
