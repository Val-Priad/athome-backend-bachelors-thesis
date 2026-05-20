from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from domain.user.user_repository import UserRepository
from infrastructure.db import db_session


class ResendVerificationUseCase:
    def __init__(
        self,
        email_verification_service: EmailVerificationService,
        user_repository: UserRepository,
    ):
        self.email_verification_service = email_verification_service
        self.user_repository = user_repository

    def execute(self, email: str) -> None:
        with db_session() as session:
            user = self.user_repository.get_user_by_email(session, email)
            self.email_verification_service.ensure_user_is_not_verified(user)
            raw_token = self.email_verification_service.get_resend_token(
                session, user.id
            )
            email_to = user.email
        self.email_verification_service.send_verification_email(
            email_to, raw_token
        )
