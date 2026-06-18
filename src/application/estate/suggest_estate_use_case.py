from uuid import UUID

from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.estate_service import EstateService
from infrastructure.db import db_session
from schemas.estate_schemas.requests.estate_create_type import EstateCreateType
from schemas.estate_schemas.requests.estate_suggest_request import (
    EstateSuggestRequest,
)
from schemas.estate_schemas.responses.estate_create_response import (
    EstateIDResponse,
)


class SuggestEstateUseCase:
    def __init__(self, estate_service: EstateService):
        self.estate_service = estate_service

    def execute(
        self,
        data: EstateSuggestRequest,
        requester_id: UUID,
    ) -> EstateIDResponse:

        vicinities = self.estate_service.get_vicinities_or_empty(data.location)

        with db_session() as session:
            creation_data = EstateCreateType(
                **data.model_dump(),
                seller_id=requester_id,
                agent_id=None,
                listing_status=ListingStatus.suggested,
            )

            estate = self.estate_service.create_estate(
                session, creation_data, vicinities
            )
            return EstateIDResponse(id=estate.id)
