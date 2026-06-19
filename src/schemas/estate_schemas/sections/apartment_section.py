from pydantic import Field

from domain.estate.enums.apartment_enums import ApartmentLayout
from schemas.parent_types import RequestValidation
from schemas.types import NonNegativeArea


class EstateApartmentSection(RequestValidation):
    apartment_layout: ApartmentLayout

    floor_number: int | None = Field(default=None, ge=0, le=200)
    has_elevator: bool | None = None

    balcony_area: NonNegativeArea | None = None
    loggia_area: NonNegativeArea | None = None
    terrace_area: NonNegativeArea | None = None
