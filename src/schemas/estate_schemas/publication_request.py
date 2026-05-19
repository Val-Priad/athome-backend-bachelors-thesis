from __future__ import annotations

from pydantic import ValidationError, model_validator
from pydantic_core import InitErrorDetails

from domain.estate.enums.estate_enums import EstateType
from domain.estate.enums.estate_listing_enums import ListingStatus
from schemas.estate_schemas.base_request import EstateBaseRequest
from schemas.estate_schemas.validators_utils import make_value_error


class EstatePublicationRequest(EstateBaseRequest):
    @model_validator(mode="after")
    def validate_for_publication(self):
        errors: list[InitErrorDetails] = []

        if self.estate_type == EstateType.apartment and self.house is not None:
            errors.append(
                make_value_error(
                    loc=("house",),
                    message="Apartment estate cannot contain house section",
                    input_value=self.house,
                )
            )

        if self.estate_type == EstateType.house and self.apartment is not None:
            errors.append(
                make_value_error(
                    loc=("apartment",),
                    message="House estate cannot contain apartment section",
                    input_value=self.apartment,
                )
            )

        if self.listing is None:
            errors.append(
                make_value_error(
                    loc=("listing",),
                    message="Listing is required for publication",
                )
            )
        elif self.listing.status != ListingStatus.active:
            errors.append(
                make_value_error(
                    loc=("listing", "status"),
                    message="Listing status must be active for publication",
                    input_value=self.listing.status,
                )
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

        for section in missing_sections:
            errors.append(
                make_value_error(
                    loc=(section,),
                    message=f"{section} is required for publication",
                )
            )

        for field in missing_fields:
            loc = tuple(field.split("."))
            errors.append(
                make_value_error(
                    loc=loc,
                    message=f"{field} is required for publication",
                )
            )

        if errors:
            raise ValidationError.from_exception_data(
                title=type(self).__name__,
                line_errors=errors,
            )

        return self


# TODO: vicinity table
# TODO: translations table
# TODO: media table
