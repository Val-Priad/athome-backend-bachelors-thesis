from uuid import UUID

from domain.user.user_repository import UserRepository
from infrastructure.db import db_session
from schemas.me_schemas.me_responses import MeResponse


class GetMeUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: UUID) -> MeResponse:
        with db_session() as session:
            user = self.user_repository.get_user_by_id(session, user_id)
            return MeResponse.from_model(user)
