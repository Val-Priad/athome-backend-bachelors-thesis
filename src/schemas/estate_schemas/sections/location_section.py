from pydantic import Field

from domain.estate.enums.estate_location_enums import Region
from schemas.parent_types import RequestValidation


class EstateLocationSection(RequestValidation):
    region: Region | None = None
    city: str | None = Field(default=None, min_length=1, max_length=255)
    street: str | None = Field(default=None, min_length=1, max_length=255)
    house_number: str | None = Field(default=None, min_length=1, max_length=50)

    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
