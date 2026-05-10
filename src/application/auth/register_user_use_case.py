from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from domain.user.services.auth_service import AuthService
from schemas.auth_schemas.auth_requests import EmailPasswordRequest


class RegisterUserUseCase:
    """Use Case для регистрации пользователя."""

    def __init__(
        self,
        auth_service: AuthService,
        email_verification_service: EmailVerificationService,
    ):
        self.auth_service = auth_service
        self.email_verification_service = email_verification_service

    def execute(self, data: EmailPasswordRequest) -> None:
        """
        Регистрирует пользователя и отправляет письмо верификации.

        Args:
            data: Данные регистрации (email, password)
        """
        from infrastructure.db import db_session

        with db_session() as session:
            user = self.auth_service.create_user(
                session, data.email, data.password
            )
            raw_token = self.email_verification_service.create_token(
                session, user.id
            )
            email_to = user.email

        self.email_verification_service.send_verification_email(
            email_to, raw_token
        )
