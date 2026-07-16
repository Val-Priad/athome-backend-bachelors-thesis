from pydantic import ConfigDict, Field

from domain.estate.enums.apartment_enums import ApartmentLayout
from domain.estate.enums.estate_enums import EstateType
from domain.estate.enums.estate_media_enums import MediaType
from domain.estate.enums.estate_pricing_enums import PriceUnit
from domain.estate.enums.house_enums import HouseType, RoomCount
from domain.estate.estate_model import Estate
from domain.estate.models.estate_media_model import EstateMedia
from schemas.estate_schemas.responses.estate_media_response import (
    EstateMediaResponse,
)
from schemas.parent_types import ResponseValidation
from schemas.types import ID, PositiveArea, PositiveMoneyAmount


class EstateFilterItem(ResponseValidation):
    id: ID
    estate_type: EstateType

    apartment_layout: ApartmentLayout | None
    room_count: RoomCount | None
    house_type: HouseType | None

    usable_area: PositiveArea
    preview: EstateMediaResponse | None

    price: PositiveMoneyAmount
    price_unit: PriceUnit

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_repo_result(cls, estate: Estate):
        preview = cls._get_preview(estate.media)

        return cls(
            id=estate.id,
            estate_type=estate.estate_type,
            apartment_layout=(
                estate.apartment.apartment_layout
                if estate.apartment is not None
                else None
            ),
            room_count=(
                estate.house.room_count if estate.house is not None else None
            ),
            house_type=(
                estate.house.house_type if estate.house is not None else None
            ),
            usable_area=estate.details.usable_area,
            preview=(
                EstateMediaResponse.from_model(preview)
                if preview is not None
                else None
            ),
            price=estate.pricing.price,
            price_unit=estate.pricing.price_unit,
        )

    @staticmethod
    def _get_preview(media: list[EstateMedia]) -> EstateMedia | None:
        return next(
            (
                item
                for item in sorted(media, key=lambda item: item.position)
                if item.media_type == MediaType.image
            ),
            None,
        )


class EstateFilterResponse(ResponseValidation):
    items: list[EstateFilterItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
