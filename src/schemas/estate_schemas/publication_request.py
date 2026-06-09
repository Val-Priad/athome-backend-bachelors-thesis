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

        self._validate_estate_type_sections(errors)
        self._validate_listing(errors)
        self._validate_common_required_sections(errors)
        self._validate_type_specific_required_sections(errors)
        self._validate_translations(errors)
        self._validate_media(errors)

        if errors:
            raise ValidationError.from_exception_data(
                title=type(self).__name__,
                line_errors=errors,
            )

        return self

    def _validate_estate_type_sections(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
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

    def _validate_listing(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.listing is None:
            errors.append(
                make_value_error(
                    loc=("listing",),
                    message="Listing is required for publication",
                )
            )
            return

        if self.listing.status != ListingStatus.active:
            errors.append(
                make_value_error(
                    loc=("listing", "status"),
                    message="Listing status must be active for publication",
                    input_value=self.listing.status,
                )
            )

    def _validate_common_required_sections(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        self._validate_location(errors)
        self._validate_pricing(errors)
        self._validate_details(errors)
        self._validate_broker(errors)

    def _validate_location(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.location is None:
            errors.append(
                make_value_error(
                    loc=("location",),
                    message="location is required for publication",
                )
            )
            return

        self._require_field(
            errors,
            value=self.location.region,
            loc=("location", "region"),
            message="location.region is required for publication",
        )
        self._require_field(
            errors,
            value=self.location.city,
            loc=("location", "city"),
            message="location.city is required for publication",
        )

    def _validate_pricing(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.pricing is None:
            errors.append(
                make_value_error(
                    loc=("pricing",),
                    message="pricing is required for publication",
                )
            )
            return

        self._require_field(
            errors,
            value=self.pricing.price,
            loc=("pricing", "price"),
            message="pricing.price is required for publication",
        )
        self._require_field(
            errors,
            value=self.pricing.price_unit,
            loc=("pricing", "price_unit"),
            message="pricing.price_unit is required for publication",
        )

    def _validate_details(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.details is None:
            errors.append(
                make_value_error(
                    loc=("details",),
                    message="details is required for publication",
                )
            )
            return

        self._require_field(
            errors,
            value=self.details.usable_area,
            loc=("details", "usable_area"),
            message="details.usable_area is required for publication",
        )

    def _validate_type_specific_required_sections(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.estate_type == EstateType.apartment:
            self._validate_apartment(errors)
            return

        if self.estate_type == EstateType.house:
            self._validate_house(errors)

    def _validate_apartment(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.apartment is None:
            errors.append(
                make_value_error(
                    loc=("apartment",),
                    message="apartment is required for publication",
                )
            )
            return

        self._require_field(
            errors,
            value=self.apartment.apartment_layout,
            loc=("apartment", "apartment_layout"),
            message="apartment.apartment_layout is required for publication",
        )

    def _validate_house(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if self.house is None:
            errors.append(
                make_value_error(
                    loc=("house",),
                    message="house is required for publication",
                )
            )
            return

        self._require_field(
            errors,
            value=self.house.room_count,
            loc=("house", "room_count"),
            message="house.room_count is required for publication",
        )
        self._require_field(
            errors,
            value=self.house.house_type,
            loc=("house", "house_type"),
            message="house.house_type is required for publication",
        )

    def _validate_translations(self, errors: list[InitErrorDetails]) -> None:
        if not self.translations:
            errors.append(
                make_value_error(
                    loc=("translations",),
                    message="At least one translation is required for publication",
                    input_value=self.translations,
                )
            )

    def _validate_media(self, errors: list[InitErrorDetails]):
        if not self.media:
            errors.append(
                make_value_error(
                    loc=("media",),
                    message="At least one media is required for publication",
                    input_value=self.media,
                )
            )

    def _validate_broker(self, errors: list[InitErrorDetails]) -> None:
        if self.broker_id is None:
            errors.append(
                make_value_error(
                    loc=("broker_id",),
                    message="broker_id is required for publication",
                    input_value=self.broker_id,
                )
            )

    @staticmethod
    def _require_field(
        errors: list[InitErrorDetails],
        *,
        value: object,
        loc: tuple[str, ...],
        message: str,
    ) -> None:
        if value is None:
            errors.append(
                make_value_error(
                    loc=loc,
                    message=message,
                )
            )
