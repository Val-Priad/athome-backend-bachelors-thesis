from uuid import UUID

from domain.user.services.me_service import MeService
from infrastructure.db import db_session


class UpdatePasswordUseCase:
    def __init__(self, me_service: MeService):
        self.me_service = me_service

    def execute(self, user_id: UUID, old_password: str, new_password: str) -> None:
        with db_session() as session:
            self.me_service.verify_password(session, user_id, old_password)
            self.me_service.ensure_new_password_differs(old_password, new_password)
            self.me_service.update_password(session, user_id, new_password)
