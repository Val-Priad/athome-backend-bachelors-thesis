from datetime import date

from pydantic import Field, model_validator
from pydantic_core import InitErrorDetails

from domain.estate.enums.house_enums import HouseType, RoomCount
from schemas.estate_schemas.validators_utils import make_value_error
from schemas.parent_types import RequestValidation
from schemas.types import NonNegativeArea


class EstateHouseSection(RequestValidation):
    room_count: RoomCount
    house_type: HouseType

    acceptance_year: int | None = Field(default=None)
    floors: int = Field(ge=1, le=200)
    underground_floors: int | None = Field(default=None, ge=0, le=20)
    parking_lots_count: int | None = Field(default=None, ge=0, le=250)

    garden_area: NonNegativeArea | None = None
    building_area: NonNegativeArea | None = None
    pool_area: NonNegativeArea | None = None
    cellar_area: NonNegativeArea | None = None
    garage_area: NonNegativeArea | None = None

    @model_validator(mode="after")
    def _validate_acceptance_year(self):
        errors: list[InitErrorDetails] = []

        if self.acceptance_year is not None:
            current_year = date.today().year
            if not (1800 <= self.acceptance_year <= current_year + 10):
                errors.append(
                    make_value_error(
                        loc=("acceptance_year",),
                        message="acceptance_year must be between 1800 and current year + 10",
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
