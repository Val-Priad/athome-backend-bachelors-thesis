from pydantic import ConfigDict, Field, ValidationError, model_validator
from pydantic_core import InitErrorDetails

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
from schemas.estate_schemas.validators_utils import make_value_error
from schemas.parent_types import RequestValidation


class EstateSuggestRequest(RequestValidation):
    model_config = ConfigDict(extra="forbid")

    estate_type: EstateType
    offer_type: OfferType

    location: EstateLocationSection
    pricing: EstatePricingSection
    details: EstateDetailsSection
    utilities: EstateUtilitiesSection | None = None
    listing: EstateListingSection

    apartment: EstateApartmentSection | None = None
    house: EstateHouseSection | None = None

    translations: list[EstateTranslationSection] = Field(min_length=1)
    media: list[EstateMediaSection] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_for_creation(self):
        errors: list[InitErrorDetails] = []

        self._validate_apartment_section(errors)
        self._validate_house_section(errors)
        self._validate_main_media(errors)

        if errors:
            raise ValidationError.from_exception_data(
                title=type(self).__name__,
                line_errors=errors,
            )

        return self

    def _validate_apartment_section(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.estate_type != EstateType.apartment:
            return

        if self.apartment is None:
            errors.append(
                make_value_error(
                    loc=("apartment",),
                    message="Apartment section is required for apartment estate",
                    input_value=self.apartment,
                )
            )

        if self.house is not None:
            errors.append(
                make_value_error(
                    loc=("house",),
                    message="Apartment estate cannot contain house section",
                    input_value=self.house,
                )
            )

    def _validate_house_section(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.estate_type != EstateType.house:
            return

        if self.house is None:
            errors.append(
                make_value_error(
                    loc=("house",),
                    message="House section is required for house estate",
                    input_value=self.house,
                )
            )

        if self.apartment is not None:
            errors.append(
                make_value_error(
                    loc=("apartment",),
                    message="House estate cannot contain apartment section",
                    input_value=self.apartment,
                )
            )

    def _validate_main_media(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        main_media_count = sum(1 for m in self.media if m.is_main)

        if main_media_count != 1:
            errors.append(
                make_value_error(
                    loc=("media",),
                    message="Estate must contain exactly one main media item",
                    input_value=self.media,
                )
            )
