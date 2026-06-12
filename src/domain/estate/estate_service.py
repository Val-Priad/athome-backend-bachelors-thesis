from typing import Protocol

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
from schemas.estate_schemas.draft_request import EstateDraftRequest


class VicinityClient(Protocol):
    def fetch_vicinity(
        self,
        lat: float,
        lon: float,
        radius: int = 10000,
    ) -> object: ...


class EstateService:
    def __init__(
        self,
        estate_repository: EstateRepository,
        vicinity_client: VicinityClient,
    ):
        self.estate_repository = estate_repository
        self.vicinity_client = vicinity_client

    @staticmethod
    def _create_related_model(model_class, data):
        if data is None:
            return model_class()

        return model_class(**data.model_dump(exclude_none=True))

    def create_draft(
        self,
        session: Session,
        data: EstateDraftRequest,
    ) -> None:
        estate = Estate(
            seller_id=data.seller_id,
            broker_id=data.broker_id,
            estate_type=data.estate_type,
            offer_type=data.offer_type,
            listing=EstateListing(
                status=ListingStatus.draft,
                available_from=(
                    data.listing.available_from if data.listing else None
                ),
            ),
        )

        estate.location = self._create_related_model(
            EstateLocation, data.location
        )

        estate.pricing = self._create_related_model(
            EstatePricing, data.pricing
        )

        estate.details = self._create_related_model(
            EstateDetails, data.details
        )

        estate.utilities = self._create_related_model(
            EstateUtilities, data.utilities
        )

        estate.apartment = self._create_related_model(
            EstateApartment, data.apartment
        )

        estate.house = self._create_related_model(EstateHouse, data.house)

        estate.translations = [
            EstateTranslation(**translation.model_dump())
            for translation in data.translations
        ]

        estate.media = [
            EstateMedia(**media.model_dump()) for media in data.media
        ]

        estate.vicinities = self._create_vicinities(data)

        return self.estate_repository.add(session, estate)

    def _create_vicinities(
        self, data: EstateDraftRequest
    ) -> list[EstateVicinity]:
        if data.location is None:
            return []

        latitude = data.location.latitude
        longitude = data.location.longitude
        if latitude is None or longitude is None:
            return []

        result = self.vicinity_client.fetch_vicinity(latitude, longitude)
        if not getattr(result, "ok", False):
            return []

        grouped_places = getattr(result, "data", None) or {}
        vicinities: list[EstateVicinity] = []

        for vicinity_type, places in grouped_places.items():
            if getattr(vicinity_type, "value", None) == "closest":
                continue

            for place in places:
                vicinities.append(
                    EstateVicinity(
                        type=place.type,
                        name=place.name,
                        latitude=place.latitude,
                        longitude=place.longitude,
                        distance_m=place.distance_m,
                    )
                )

        return vicinities
