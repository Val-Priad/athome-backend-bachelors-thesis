from datetime import date

from pydantic import model_validator

from domain.estate.enums.estate_listing_enums import ListingStatus
from schemas.parent_types import RequestValidation


class EstateListingSection(RequestValidation):
    status: ListingStatus
    available_from: date | None = None

    @model_validator(mode="after")
    def _validate_available_from(self):
        if self.available_from is None:
            return self
        if self.available_from < date.today():
            raise ValueError("available_from cannot be in the past")
        return self
