from application.ports.transaction_manager import TransactionManagerProtocol
from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from domain.user.services.auth_service import AuthService
from schemas.auth_schemas.auth_requests import EmailPasswordRequest


class RegisterUserUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        auth_service: AuthService,
        email_verification_service: EmailVerificationService,
    ) -> None:
        self._transactions = transactions
        self._auth_service = auth_service
        self._email_verification_service = email_verification_service

    def execute(self, data: EmailPasswordRequest) -> None:
        with self._transactions.session() as session:
            user = self._auth_service.create_user(
                session, data.email, data.password
            )
            raw_token = self._email_verification_service.create_token(
                session, user.id
            )
            email_to = user.email
        self._email_verification_service.send_verification_email(
            email_to, raw_token
        )
