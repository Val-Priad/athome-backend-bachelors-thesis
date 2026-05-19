from pydantic import Field

from domain.estate.enums.estate_enums import EstateType, OfferType
from schemas.estate_schemas.sections.apartment_section import (
    EstateApartmentSection,
)
from schemas.estate_schemas.sections.details_section import (
    EstateDetailsSection,
)
from schemas.estate_schemas.sections.house_section import EstateHouseSection
from schemas.estate_schemas.sections.listing_section import (
    EstateListingSection,
)
from schemas.estate_schemas.sections.location_section import (
    EstateLocationSection,
)
from schemas.estate_schemas.sections.media_section import EstateMediaSection
from schemas.estate_schemas.sections.pricing_section import (
    EstatePricingSection,
)
from schemas.estate_schemas.sections.translation_section import (
    EstateTranslationSection,
)
from schemas.estate_schemas.sections.utilities_section import (
    EstateUtilitiesSection,
)
from schemas.parent_types import RequestValidation


class EstateBaseRequest(RequestValidation):
    estate_type: EstateType
    offer_type: OfferType

    location: EstateLocationSection | None = None
    pricing: EstatePricingSection | None = None
    details: EstateDetailsSection | None = None
    utilities: EstateUtilitiesSection | None = None
    listing: EstateListingSection | None = None

    apartment: EstateApartmentSection | None = None
    house: EstateHouseSection | None = None

    translations: list[EstateTranslationSection] = Field(default_factory=list)
    media: list[EstateMediaSection] = Field(default_factory=list)
