from application.ports.transaction_manager import TransactionManagerProtocol
from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)


class VerifyEmailUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        email_verification_service: EmailVerificationService,
    ) -> None:
        self._transactions = transactions
        self._email_verification_service = email_verification_service

    def execute(self, token: str) -> None:
        with self._transactions.session() as session:
            self._email_verification_service.verify_token(session, token)
