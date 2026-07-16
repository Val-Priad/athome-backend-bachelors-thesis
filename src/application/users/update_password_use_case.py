from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.user.services.me_service import MeService


class UpdatePasswordUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        me_service: MeService,
    ) -> None:
        self._transactions = transactions
        self._me_service = me_service

    def execute(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> None:
        with self._transactions.session() as session:
            self._me_service.verify_password(session, user_id, old_password)
            self._me_service.ensure_new_password_differs(
                old_password, new_password
            )
            self._me_service.update_password(session, user_id, new_password)
