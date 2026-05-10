from uuid import UUID

from domain.user.services.me_service import MeService
from infrastructure.db import db_session
from schemas.me_schemas.me_requests import UpdateUserPersonalDataRequest
from schemas.me_schemas.me_responses import MeResponse


class UpdatePersonalDataUseCase:
    def __init__(self, me_service: MeService):
        self.me_service = me_service

    def execute(self, user_id: UUID, data: UpdateUserPersonalDataRequest) -> MeResponse:
        with db_session() as session:
            user = self.me_service.update_personal_data(session, user_id, data)
            return MeResponse.from_model(user)
