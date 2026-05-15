from datetime import date

from pydantic import Field, model_validator

from domain.estate.enums.house_enums import HouseType, RoomCount
from schemas.parent_types import RequestValidation


class EstateHouseSection(RequestValidation):
    room_count: RoomCount | None = None
    house_type: HouseType | None = None

    acceptance_year: int | None = Field(default=None, ge=0)
    floors: int | None = Field(default=None, ge=0)
    underground_floors: int | None = Field(default=None, ge=0)
    parking_lots_count: int | None = Field(default=None, ge=0)

    garden_area: float | None = Field(default=None, ge=0)
    building_area: float | None = Field(default=None, ge=0)
    pool_area: float | None = Field(default=None, ge=0)
    cellar_area: float | None = Field(default=None, ge=0)
    garage_area: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _validate_acceptance_year(self):
        if self.acceptance_year is None:
            return self
        current_year = date.today().year
        if not (1800 <= self.acceptance_year <= current_year):
            raise ValueError(
                "acceptance_year must be between 1800 and current year"
            )
        return self
