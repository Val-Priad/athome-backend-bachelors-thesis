from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from infrastructure.db import db_session


class ResendVerificationUseCase:
    def __init__(self, email_verification_service: EmailVerificationService):
        self.email_verification_service = email_verification_service

    def execute(self, email: str) -> None:
        with db_session() as session:
            user = self.email_verification_service.get_user_by_email(session, email)
            self.email_verification_service.ensure_user_is_not_verified(user)
            raw_token = self.email_verification_service.get_resend_token(
                session, user.id
            )
            self.email_verification_service.send_verification_email(
                user.email, raw_token
            )
