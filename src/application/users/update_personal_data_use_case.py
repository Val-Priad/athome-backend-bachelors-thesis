from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.user.services.me_service import MeService
from schemas.me_schemas.me_requests import UpdateUserPersonalDataRequest
from schemas.me_schemas.me_responses import MeResponse


class UpdatePersonalDataUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        me_service: MeService,
    ) -> None:
        self._transactions = transactions
        self._me_service = me_service

    def execute(
        self, user_id: UUID, data: UpdateUserPersonalDataRequest
    ) -> MeResponse:
        with self._transactions.session() as session:
            updates = data.model_dump(exclude_unset=True)
            user = self._me_service.update_personal_data(
                session, user_id, updates
            )
            return MeResponse.from_model(user)
