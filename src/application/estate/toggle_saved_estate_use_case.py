from uuid import UUID

from domain.estate.estate_repository import EstateRepository
from exceptions.custom_exceptions.estate_exceptions import EstateNotFoundError
from infrastructure.db import db_session


class ToggleSavedEstateUseCase:
    def __init__(self, estate_repository: EstateRepository) -> None:
        self.estate_repository = estate_repository

    def execute(self, requester_id: UUID, estate_id: UUID) -> None:
        with db_session() as session:
            if not self.estate_repository.estate_exists(session, estate_id):
                raise EstateNotFoundError()

            self.estate_repository.toggle_saved(
                session, requester_id, estate_id
            )
