from application.ports.transaction_manager import TransactionManagerProtocol
from domain.password_reset.password_reset_service import PasswordResetService


class VerifyNewPasswordUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        password_reset_service: PasswordResetService,
    ) -> None:
        self._transactions = transactions
        self._password_reset_service = password_reset_service

    def execute(self, token: str, password: str) -> None:
        with self._transactions.session() as session:
            self._password_reset_service.reset_password(
                session, token, password
            )
