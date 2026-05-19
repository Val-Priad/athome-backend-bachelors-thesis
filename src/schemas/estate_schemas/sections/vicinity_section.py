from pydantic import Field

from domain.estate.enums.estate_vicinity_enums import VicinityType
from schemas.parent_types import RequestValidation


class EstateVicinitySection(RequestValidation):
    type: VicinityType
    name: str = Field(min_length=1, max_length=255)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    distance_m: int = Field(ge=0)
