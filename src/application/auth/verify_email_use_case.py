from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from infrastructure.db import db_session


class VerifyEmailUseCase:
    def __init__(self, email_verification_service: EmailVerificationService):
        self.email_verification_service = email_verification_service

    def execute(self, token: str) -> None:
        with db_session() as session:
            self.email_verification_service.verify_token(session, token)
