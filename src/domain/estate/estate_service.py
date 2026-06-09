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
from schemas.estate_schemas.draft_request import EstateDraftRequest


class EstateService:
    def __init__(self, estate_repository: EstateRepository):
        self.estate_repository = estate_repository

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

        return self.estate_repository.add(session, estate)
