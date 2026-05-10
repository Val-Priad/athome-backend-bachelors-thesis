from domain.password_reset.password_reset_service import (
    PasswordResetService,
)
from infrastructure.db import db_session


class VerifyNewPasswordUseCase:
    """Use Case для подтверждения нового пароля."""

    def __init__(self, password_reset_service: PasswordResetService):
        self.password_reset_service = password_reset_service

    def execute(self, token: str, password: str) -> None:
        """
        Сбрасывает пароль по токену.

        Args:
            token: Токен сброса пароля
            password: Новый пароль
        """
        with db_session() as session:
            self.password_reset_service.reset_password(
                session, token, password
            )
