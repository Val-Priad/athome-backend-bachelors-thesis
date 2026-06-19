from domain.estate.estate_service import EstateService
from infrastructure.db import db_session
from schemas.estate_schemas.responses.estate_filter_response import (
    EstateFilterResponse,
)


class GetFilteredEstateUseCase:
    def __init__(self, estate_service: EstateService) -> None:
        self.estate_service = estate_service

    def execute(self, filters, requester_id) -> EstateFilterResponse:
        with db_session() as session:
            return self.estate_service.get_filtered_estate(
                session, filters, requester_id
            )
