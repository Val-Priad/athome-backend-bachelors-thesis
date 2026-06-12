from datetime import datetime, timezone

from sqlalchemy.orm import Session

from domain.estate.enums.estate_enums import EstateType
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
from domain.user.user_model import UserRole
from infrastructure.vicinity.vicinity_protocol import VicinityClientProtocol
from schemas.estate_schemas.create_request import EstateCreateRequest


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
        data: EstateCreateRequest,
        requester_role: UserRole = UserRole.admin,
    ) -> None:
        listing_status = (
            ListingStatus.active
            if requester_role == UserRole.admin
            else ListingStatus.suggested
        )

        estate = Estate(
            seller_id=data.seller_id,
            broker_id=data.broker_id,
            estate_type=data.estate_type,
            offer_type=data.offer_type,
            listing=self._create_listing(
                status=listing_status,
                available_from=data.listing.available_from,
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

        if data.utilities is not None:
            estate.utilities = self._create_related_model(
                EstateUtilities, data.utilities
            )

        if data.estate_type == EstateType.apartment:
            estate.apartment = self._create_related_model(
                EstateApartment, data.apartment
            )

        if data.estate_type == EstateType.house:
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
        self, data: EstateCreateRequest
    ) -> list[EstateVicinity]:
        if data.location is None:
            return []

        latitude = data.location.latitude
        longitude = data.location.longitude
        if latitude is None or longitude is None:
            return []

        result = self.vicinity_client.fetch_vicinity(latitude, longitude)
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
