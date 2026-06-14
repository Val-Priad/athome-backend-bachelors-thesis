from pydantic import Field

from domain.estate.enums.apartment_enums import ApartmentLayout
from schemas.parent_types import RequestValidation


class EstateApartmentSection(RequestValidation):
    apartment_layout: ApartmentLayout

    floor_number: int | None = Field(default=None, ge=0)
    has_elevator: bool | None = None

    balcony_area: float | None = Field(default=None, ge=0)
    loggia_area: float | None = Field(default=None, ge=0)
    terrace_area: float | None = Field(default=None, ge=0)
