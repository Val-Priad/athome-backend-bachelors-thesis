from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from infrastructure.db import db_session


class VerifyEmailUseCase:
    """Use Case для верификации email по токену."""

    def __init__(self, email_verification_service: EmailVerificationService):
        self.email_verification_service = email_verification_service

    def execute(self, token: str) -> None:
        """
        Верифицирует email пользователя по токену.

        Args:
            token: Токен верификации
        """
        with db_session() as session:
            self.email_verification_service.verify_token(session, token)
