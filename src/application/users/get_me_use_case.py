from uuid import UUID

from domain.user.services.me_service import MeService
from infrastructure.db import db_session
from schemas.me_schemas.me_responses import MeResponse


class GetMeUseCase:
    """Use Case для получения данных текущего пользователя."""

    def __init__(self, me_service: MeService):
        self.me_service = me_service

    def execute(self, user_id: UUID) -> MeResponse:
        """
        Получает данные текущего пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            MeResponse с данными пользователя
        """
        with db_session() as session:
            user = self.me_service.get_user_by_id(session, user_id)
            return MeResponse.from_model(user)
