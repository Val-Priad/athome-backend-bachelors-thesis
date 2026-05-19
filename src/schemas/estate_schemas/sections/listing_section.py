
from datetime import date

from pydantic import ValidationError, model_validator
from pydantic_core import InitErrorDetails

from domain.estate.enums.estate_listing_enums import ListingStatus
from schemas.estate_schemas.validators_utils import make_value_error
from schemas.parent_types import RequestValidation


class EstateListingSection(RequestValidation):
    status: ListingStatus
    available_from: date | None = None

    @model_validator(mode="after")
    def _validate_available_from(self):
        errors: list[InitErrorDetails] = []

        if (
            self.available_from is not None
            and self.available_from < date.today()
        ):
            errors.append(
                make_value_error(
                    loc=("available_from",),
                    message="available_from cannot be in the past",
                    input_value=self.available_from,
                )
            )

        if errors:
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=errors,
            )

        return self
