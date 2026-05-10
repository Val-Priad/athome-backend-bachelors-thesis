from uuid import UUID

from domain.user.services.me_service import MeService
from infrastructure.db import db_session


class DeleteMeUseCase:
    """Use Case для удаления аккаунта текущего пользователя."""

    def __init__(self, me_service: MeService):
        self.me_service = me_service

    def execute(self, user_id: UUID) -> None:
        """
        Удаляет аккаунт пользователя.

        Args:
            user_id: ID пользователя
        """
        with db_session() as session:
            self.me_service.delete_user_by_id(session, user_id)
