from typing import cast

from pydantic import ValidationError, model_validator
from pydantic_core import InitErrorDetails

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_listing_enums import ListingStatus
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
from schemas.estate_schemas.sections.pricing_section import (
    EstatePricingSection,
)
from schemas.estate_schemas.sections.utilities_section import (
    EstateUtilitiesSection,
)
from schemas.parent_types import RequestValidation


class EstatePublicationRequest(RequestValidation):
    estate_type: EstateType
    offer_type: OfferType

    location: EstateLocationSection | None = None
    pricing: EstatePricingSection | None = None
    details: EstateDetailsSection | None = None
    utilities: EstateUtilitiesSection | None = None
    listing: EstateListingSection | None = None

    apartment: EstateApartmentSection | None = None
    house: EstateHouseSection | None = None

    @model_validator(mode="after")
    def validate_for_publication(self):
        if self.estate_type == EstateType.apartment and self.house is not None:
            raise ValueError("Apartment estate cannot contain house section")

        if self.estate_type == EstateType.house and self.apartment is not None:
            raise ValueError("House estate cannot contain apartment section")

        if self.listing is None or self.listing.status != ListingStatus.active:
            raise ValueError(
                "Listing with status 'active' is required for publication"
            )

        missing_sections: list[str] = []
        missing_fields: list[str] = []

        if self.location is None:
            missing_sections.append("location")
        else:
            if self.location.region is None:
                missing_fields.append("location.region")
            if self.location.city is None:
                missing_fields.append("location.city")

        if self.pricing is None:
            missing_sections.append("pricing")
        else:
            if self.pricing.price is None:
                missing_fields.append("pricing.price")
            if self.pricing.price_unit is None:
                missing_fields.append("pricing.price_unit")

        if self.details is None:
            missing_sections.append("details")
        else:
            if self.details.usable_area is None:
                missing_fields.append("details.usable_area")

        if self.estate_type == EstateType.apartment:
            if self.apartment is None:
                missing_sections.append("apartment")
            elif self.apartment.apartment_layout is None:
                missing_fields.append("apartment.apartment_layout")

        if self.estate_type == EstateType.house:
            if self.house is None:
                missing_sections.append("house")
            else:
                if self.house.room_count is None:
                    missing_fields.append("house.room_count")
                if self.house.house_type is None:
                    missing_fields.append("house.house_type")

        if missing_sections or missing_fields:
            errors: list[InitErrorDetails] = []

            for section in missing_sections:
                errors.append(
                    cast(
                        InitErrorDetails,
                        {
                            "type": "value_error",
                            "loc": (section,),
                            "input": None,
                            "ctx": {
                                "error": ValueError(
                                    "Section is required for publication"
                                )
                            },
                        },
                    )
                )

            for field in missing_fields:
                loc = tuple(field.split("."))
                errors.append(
                    cast(
                        InitErrorDetails,
                        {
                            "type": "value_error",
                            "loc": loc,
                            "input": None,
                            "ctx": {
                                "error": ValueError(
                                    "Field is required for publication"
                                )
                            },
                        },
                    )
                )

            raise ValidationError.from_exception_data(
                title=type(self).__name__,
                line_errors=errors,
            )

        return self
