from pydantic import Field

from domain.estate.enums.estate_location_enums import Region
from schemas.parent_types import RequestValidation
from schemas.types import Latitude, Longitude


class EstateLocationSection(RequestValidation):
    region: Region
    city: str = Field(min_length=1, max_length=255)
    street: str = Field(min_length=1, max_length=255)
    house_number: str | None = Field(default=None, min_length=1, max_length=50)

    latitude: Latitude
    longitude: Longitude
