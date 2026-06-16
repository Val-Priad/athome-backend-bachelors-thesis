from datetime import datetime, timezone

from sqlalchemy.orm import Session

from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.estate_model import Estate
from domain.estate.estate_repository import EstateRepository
from domain.estate.models.estate_apartment_model import EstateApartment
from domain.estate.models.estate_details_model import EstateDetails
from domain.estate.models.estate_house_model import EstateHouse
from domain.estate.models.estate_listing_model import EstateListing
from domain.estate.models.estate_location_model import EstateLocation
from domain.estate.models.estate_media_model import EstateMedia
from domain.estate.models.estate_pricing_model import EstatePricing
from domain.estate.models.estate_translation_model import EstateTranslation
from domain.estate.models.estate_utilities_model import EstateUtilities
from domain.estate.models.estate_vicinity_model import EstateVicinity
from infrastructure.vicinity.vicinity_protocol import VicinityClientProtocol
from schemas.estate_schemas.estate_create_type import EstateCreateType
from schemas.estate_schemas.sections.location_section import (
    EstateLocationSection,
)


class EstateService:
    def __init__(
        self,
        estate_repository: EstateRepository,
        vicinity_client: VicinityClientProtocol,
    ):
        self.estate_repository = estate_repository
        self.vicinity_client = vicinity_client

    @staticmethod
    def _create_related_model(model_class, data):
        return model_class(**data.model_dump(exclude_none=True))

    @staticmethod
    def _create_listing(
        status: ListingStatus,
        available_from,
    ) -> EstateListing:
        return EstateListing(
            status=status,
            published_at=(
                datetime.now(timezone.utc)
                if status == ListingStatus.active
                else None
            ),
            available_from=available_from,
        )

    def create_estate(
        self,
        session: Session,
        data: EstateCreateType,
        vicinities: list[EstateVicinity],
    ) -> Estate:
        estate = Estate(
            seller_id=data.seller_id,
            agent_id=data.agent_id,
            estate_type=data.estate_type,
            offer_type=data.offer_type,
            listing=self._create_listing(
                status=data.listing_status,
                available_from=data.listing.available_from,
            ),
            location=self._create_related_model(
                EstateLocation,
                data.location,
            ),
            pricing=self._create_related_model(
                EstatePricing,
                data.pricing,
            ),
            details=self._create_related_model(
                EstateDetails,
                data.details,
            ),
            utilities=(
                self._create_related_model(EstateUtilities, data.utilities)
                if data.utilities is not None
                else EstateUtilities()
            ),
            translations=[
                EstateTranslation(**translation.model_dump())
                for translation in data.translations
            ],
            media=[EstateMedia(**media.model_dump()) for media in data.media],
        )

        if data.apartment is not None:
            estate.apartment = self._create_related_model(
                EstateApartment,
                data.apartment,
            )

        if data.house is not None:
            estate.house = self._create_related_model(
                EstateHouse,
                data.house,
            )

        estate.vicinities = vicinities

        return self.estate_repository.add(session, estate)

    def get_vicinities_or_empty(
        self,
        location: EstateLocationSection,
    ) -> list[EstateVicinity]:
        result = self.vicinity_client.fetch_vicinity(
            location.latitude,
            location.longitude,
        )

        if not result.ok:
            return []

        grouped_places = result.data or {}
        vicinities: list[EstateVicinity] = []

        for vicinity_type, places in grouped_places.items():
            for place in places:
                vicinities.append(
                    EstateVicinity(
                        type=vicinity_type,
                        name=place.name,
                        latitude=place.latitude,
                        longitude=place.longitude,
                        distance_m=place.distance_m,
                    )
                )

        return vicinities
