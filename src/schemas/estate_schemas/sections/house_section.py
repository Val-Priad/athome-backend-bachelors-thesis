from __future__ import annotations

from datetime import date

from pydantic import Field, model_validator
from pydantic_core import InitErrorDetails

from domain.estate.enums.house_enums import HouseType, RoomCount
from schemas.estate_schemas.validators_utils import make_value_error
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
        errors: list[InitErrorDetails] = []

        if self.acceptance_year is not None:
            current_year = date.today().year
            if not (1800 <= self.acceptance_year <= current_year):
                errors.append(
                    make_value_error(
                        loc=("acceptance_year",),
                        message="acceptance_year must be between 1800 and current year",
                        input_value=self.acceptance_year,
                    )
                )

        if errors:
            from pydantic import ValidationError

            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=errors,
            )

        return self
