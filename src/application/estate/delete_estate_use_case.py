from domain.estate.estate_repository import EstateRepository
from domain.user.user_model import UserRole
from infrastructure.db import db_session
from security.authorization import AuthorizationService


class DeleteEstateUseCase:
    def __init__(
        self,
        estate_repository: EstateRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self.estate_repository = estate_repository
        self.authorization_service = authorization_service

    def execute(self, estate_id, requester_id):
        with db_session() as session:
            self.authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self.estate_repository.delete_estate_by_id(session, estate_id)
