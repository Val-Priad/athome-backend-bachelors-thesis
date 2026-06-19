from pydantic import ConfigDict, Field

from domain.estate.enums.apartment_enums import ApartmentLayout
from domain.estate.enums.estate_enums import EstateType
from domain.estate.enums.estate_pricing_enums import PriceUnit
from domain.estate.enums.house_enums import HouseType, RoomCount
from schemas.estate_schemas.sections.media_section import EstateMediaSection
from schemas.parent_types import ResponseValidation
from schemas.types import ID, PositiveArea, PositiveMoneyAmount


class EstateFilterItem(ResponseValidation):
    id: ID
    estate_type: EstateType
    apartment_layout: ApartmentLayout | None
    room_count: RoomCount | None
    house_type: HouseType | None
    usable_area: PositiveArea
    main_media: EstateMediaSection
    price: PositiveMoneyAmount
    price_unit: PriceUnit

    model_config = ConfigDict(from_attributes=True)


class EstateFilterResponse(ResponseValidation):
    items: list[EstateFilterItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
