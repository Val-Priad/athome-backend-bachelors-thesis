from uuid import UUID

from domain.user.user_repository import UserRepository
from infrastructure.db import db_session


class DeleteMeUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: UUID) -> None:
        with db_session() as session:
            session.delete(
                self.user_repository.get_user_by_id(session, user_id)
            )
