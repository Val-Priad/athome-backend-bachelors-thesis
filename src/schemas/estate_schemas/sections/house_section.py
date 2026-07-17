from pydantic import Field

from domain.estate.enums.house_enums import HouseType, RoomCount
from schemas.parent_types import RequestValidation
from schemas.types import AcceptanceYear, NonNegativeArea


class EstateHouseSection(RequestValidation):
    room_count: RoomCount
    house_type: HouseType

    acceptance_year: AcceptanceYear | None = None
    floors: int = Field(ge=1, le=200)
    underground_floors: int | None = Field(default=None, ge=0, le=20)
    parking_lots_count: int | None = Field(default=None, ge=0, le=250)

    garden_area: NonNegativeArea | None = None
    building_area: NonNegativeArea | None = None
    pool_area: NonNegativeArea | None = None
    cellar_area: NonNegativeArea | None = None
    garage_area: NonNegativeArea | None = None
