from domain.password_reset.password_reset_service import (
    PasswordResetService,
)
from infrastructure.db import db_session


class ResetPasswordUseCase:
    """Use Case для запроса сброса пароля."""

    def __init__(self, password_reset_service: PasswordResetService):
        self.password_reset_service = password_reset_service

    def execute(self, email: str) -> None:
        """
        Отправляет письмо с токеном сброса пароля.

        Args:
            email: Email пользователя
        """
        with db_session() as session:
            user = self.password_reset_service.get_user_by_email(
                session, email
            )
            raw_token = self.password_reset_service.get_token(session, user.id)

            self.password_reset_service.send_reset_password_email(
                email, raw_token
            )
