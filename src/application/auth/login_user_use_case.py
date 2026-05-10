from uuid import UUID

from domain.user.services.auth_service import AuthService
from infrastructure.db import db_session


class LoginUserUseCase:
    """Use Case для входа пользователя."""

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def execute(self, email: str, password: str) -> UUID:
        """
        Проверяет учетные данные и возвращает ID пользователя.

        Args:
            email: Email пользователя
            password: Пароль пользователя

        Returns:
            UUID пользователя
        """
        with db_session() as session:
            user = self.auth_service.verify_password(session, email, password)
            return user.id
