from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.estate_media_repository import EstateMediaRepository
from domain.estate.estate_service import EstateService
from domain.media.media_enums import MediaPurpose
from domain.media.media_service import MediaService
from schemas.estate_schemas.requests.estate_create_type import (
    EstateMutationType,
)
from schemas.estate_schemas.requests.estate_suggest_request import (
    EstateSuggestRequest,
)
from schemas.estate_schemas.responses.estate_create_response import (
    EstateIDResponse,
)


class SuggestEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_service: EstateService,
        media_service: MediaService,
        estate_media_repository: EstateMediaRepository,
    ) -> None:
        self._transactions = transactions
        self._estate_service = estate_service
        self._media_service = media_service
        self._estate_media_repository = estate_media_repository

    def execute(
        self,
        data: EstateSuggestRequest,
        requester_id: UUID,
    ) -> EstateIDResponse:

        vicinities = self._estate_service.get_vicinities_or_empty(
            data.location
        )

        self._media_service.validate_objects(
            media=data.media,
            uploader_id=requester_id,
            purpose=MediaPurpose.estate,
        )

        with self._transactions.session() as session:
            creation_data = EstateMutationType(
                **data.model_dump(),
                seller_id=requester_id,
                agent_id=None,
                listing_status=ListingStatus.suggested,
            )

            self._estate_media_repository.ensure_object_keys_unused(
                session,
                [item.object_key for item in data.media],
            )
            estate = self._estate_service.create_estate(
                session, creation_data, vicinities
            )
            return EstateIDResponse(id=estate.id)
