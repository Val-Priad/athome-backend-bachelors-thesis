from pydantic import Field

from domain.estate.enums.estate_vicinity_enums import VicinityType
from schemas.parent_types import RequestValidation
from schemas.types import Latitude, Longitude


class EstateVicinitySection(RequestValidation):
    type: VicinityType
    name: str = Field(min_length=1, max_length=255)

    latitude: Latitude
    longitude: Longitude
    distance_m: int = Field(ge=0, le=100_000)
