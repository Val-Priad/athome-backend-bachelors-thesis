from datetime import date, datetime
from decimal import Decimal

from pydantic import ConfigDict

from domain.estate.enums.apartment_enums import ApartmentLayout
from domain.estate.enums.estate_details_enums import (
    EnergyClass,
    Furnishing,
    PropertyCondition,
)
from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.enums.estate_location_enums import Region
from domain.estate.enums.estate_pricing_enums import PriceUnit
from domain.estate.enums.estate_vicinity_enums import VicinityType
from domain.estate.enums.house_enums import HouseType, RoomCount
from domain.estate.enums.utilities_enums import (
    HeatingSource,
    PrimaryInternetConnectionType,
)
from domain.user.user_model import UserRole
from schemas.estate_schemas.responses.estate_media_response import (
    EstateMediaResponse,
)
from schemas.parent_types import ResponseValidation
from schemas.types import (
    ID,
    E164PhoneNumberType,
    ImageKey,
    Latitude,
    Longitude,
    UserDescription,
    UserName,
)


class EstateBaseResponse(ResponseValidation):
    model_config = ConfigDict(from_attributes=True)


class EstateUserResponse(EstateBaseResponse):
    id: ID
    email: str
    role: UserRole

    name: UserName | None
    phone_number: E164PhoneNumberType | None
    avatar_key: ImageKey | None
    description: UserDescription | None


class EstateLocationResponse(EstateBaseResponse):
    region: Region
    city: str
    street: str
    house_number: str | None

    latitude: Latitude
    longitude: Longitude


class EstatePricingResponse(EstateBaseResponse):
    price: Decimal
    price_unit: PriceUnit

    cost_of_living: Decimal | None
    commission: Decimal | None
    commission_paid_by_owner: bool | None
    refundable_deposit: Decimal | None


class EstateListingResponse(EstateBaseResponse):
    status: ListingStatus
    published_at: datetime | None
    expires_at: datetime | None
    available_from: date


class EstateUtilitiesResponse(EstateBaseResponse):
    has_cold_water: bool | None
    has_hot_water: bool | None
    has_gas: bool | None
    has_sewerage: bool | None

    heating_source: HeatingSource | None
    primary_internet_connection_type: PrimaryInternetConnectionType | None


class EstateDetailsResponse(EstateBaseResponse):
    condition: PropertyCondition | None
    energy_class: EnergyClass | None

    usable_area: float
    total_property_area: float | None

    furnishing: Furnishing | None
    easy_access: bool | None


class EstateApartmentResponse(EstateBaseResponse):
    apartment_layout: ApartmentLayout

    floor_number: int | None
    has_elevator: bool | None

    balcony_area: float | None
    loggia_area: float | None
    terrace_area: float | None


class EstateHouseResponse(EstateBaseResponse):
    room_count: RoomCount
    house_type: HouseType

    acceptance_year: int | None
    floors: int
    underground_floors: int | None
    parking_lots_count: int | None

    garden_area: float | None
    building_area: float | None
    pool_area: float | None
    cellar_area: float | None
    garage_area: float | None


class EstateTranslationResponse(EstateBaseResponse):
    lang_code: str
    title: str
    description: str


class EstateVicinityResponse(EstateBaseResponse):
    id: int

    type: VicinityType
    name: str

    latitude: Latitude
    longitude: Longitude
    distance_m: int


class EstateGeneralGetResponse(EstateBaseResponse):
    id: ID

    agent_id: ID | None

    estate_type: EstateType
    offer_type: OfferType

    created_at: datetime
    updated_at: datetime

    agent: EstateUserResponse | None

    location: EstateLocationResponse
    pricing: EstatePricingResponse
    listing: EstateListingResponse
    utilities: EstateUtilitiesResponse | None
    details: EstateDetailsResponse

    apartment: EstateApartmentResponse | None
    house: EstateHouseResponse | None

    translations: list[EstateTranslationResponse]
    media: list[EstateMediaResponse]
    vicinities: list[EstateVicinityResponse]


class EstateGetResponseWithSeller(EstateGeneralGetResponse):
    seller: EstateUserResponse | None
    seller_id: ID | None
