from datetime import date
from decimal import Decimal

from pydantic import Field, model_validator

from domain.estate.enums.apartment_enums import ApartmentLayout
from domain.estate.enums.estate_details_enums import (
    EnergyClass,
    Furnishing,
    PropertyCondition,
)
from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_location_enums import Region
from domain.estate.enums.estate_pricing_enums import PriceUnit
from domain.estate.enums.house_enums import HouseType, RoomCount
from domain.estate.enums.utilities_enums import (
    HeatingSource,
    PrimaryInternetConnectionType,
)
from schemas.parent_types import RequestValidation


class EstateLocationCreateRequest(RequestValidation):
    region: Region | None = None
    city: str | None = Field(default=None, min_length=1, max_length=255)
    street: str | None = Field(default=None, min_length=1, max_length=255)
    house_number: str | None = Field(default=None, min_length=1, max_length=50)

    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class EstatePricingCreateRequest(RequestValidation):
    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    price_unit: PriceUnit | None = None

    cost_of_living: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    commission: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    commission_paid_by_owner: bool | None = None

    refundable_deposit: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )


class EstateDetailsCreateRequest(RequestValidation):
    condition: PropertyCondition | None = None
    energy_class: EnergyClass | None = None

    usable_area: float | None = Field(default=None, ge=0)
    total_property_area: float | None = Field(default=None, ge=0)

    furnishing: Furnishing | None = None
    easy_access: bool | None = None


class EstateUtilitiesCreateRequest(RequestValidation):
    has_cold_water: bool | None = None
    has_hot_water: bool | None = None
    has_gas: bool | None = None
    has_sewerage: bool | None = None

    heating_source: HeatingSource | None = None
    primary_internet_connection_type: PrimaryInternetConnectionType | None = (
        None
    )


class EstateApartmentCreateRequest(RequestValidation):
    apartment_layout: ApartmentLayout | None = None

    floor_number: int | None = Field(default=None, ge=0)
    has_elevator: bool | None = None

    balcony_area: float | None = Field(default=None, ge=0)
    loggia_area: float | None = Field(default=None, ge=0)
    terrace_area: float | None = Field(default=None, ge=0)


class EstateHouseCreateRequest(RequestValidation):
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


class EstateListingCreateRequest(RequestValidation):
    available_from: date | None = None


class CreateEstateRequest(RequestValidation):
    estate_type: EstateType
    offer_type: OfferType

    location: EstateLocationCreateRequest | None = None
    pricing: EstatePricingCreateRequest | None = None
    details: EstateDetailsCreateRequest | None = None
    utilities: EstateUtilitiesCreateRequest | None = None
    listing: EstateListingCreateRequest | None = None

    apartment: EstateApartmentCreateRequest | None = None
    house: EstateHouseCreateRequest | None = None

    @model_validator(mode="after")
    def validate_estate_composition(self):
        if self.estate_type == EstateType.apartment and self.house is not None:
            raise ValueError("Apartment estate cannot contain house section")

        if self.estate_type == EstateType.house and self.apartment is not None:
            raise ValueError("House estate cannot contain apartment section")

        return self
