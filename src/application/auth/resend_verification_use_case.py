from application.transactions import TransactionManagerProtocol
from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from domain.user.user_repository import UserRepository


class ResendVerificationUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        email_verification_service: EmailVerificationService,
        user_repository: UserRepository,
    ) -> None:
        self._transactions = transactions
        self._email_verification_service = email_verification_service
        self._user_repository = user_repository

    def execute(self, email: str) -> None:
        with self._transactions.session() as session:
            user = self._user_repository.get_user_by_email(session, email)
            self._email_verification_service.ensure_user_is_not_verified(user)
            raw_token = self._email_verification_service.get_resend_token(
                session, user.id
            )
            email_to = user.email
        self._email_verification_service.send_verification_email(
            email_to, raw_token
        )
