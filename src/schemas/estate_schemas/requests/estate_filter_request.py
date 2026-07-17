import datetime
import uuid
from enum import Enum
from typing import ClassVar

from pydantic import (
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)
from pydantic_core import InitErrorDetails

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
from schemas.estate_schemas.validators_utils import make_value_error
from schemas.parent_types import RequestValidation
from schemas.types import (
    AcceptanceYear,
    NonNegativeArea,
    NonNegativeMoneyAmount,
    PositiveArea,
)


class EstateSortBy(str, Enum):
    created_at = "created_at"
    published_at = "published_at"
    expires_at = "expires_at"
    available_from = "available_from"
    price = "price"
    usable_area = "usable_area"
    total_property_area = "total_property_area"
    floor_number = "floor_number"
    acceptance_year = "acceptance_year"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class EstateBaseFilterRequest(RequestValidation):
    model_config = ConfigDict(extra="forbid")

    RANGE_FILTERS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("created_at_from", "created_at_to"),
        ("price_from", "price_to"),
        ("cost_of_living_from", "cost_of_living_to"),
        ("published_at_from", "published_at_to"),
        ("expires_at_from", "expires_at_to"),
        ("available_from_from", "available_from_to"),
        ("usable_area_from", "usable_area_to"),
        ("total_property_area_from", "total_property_area_to"),
        ("floor_number_from", "floor_number_to"),
        ("balcony_area_from", "balcony_area_to"),
        ("loggia_area_from", "loggia_area_to"),
        ("terrace_area_from", "terrace_area_to"),
        ("acceptance_year_from", "acceptance_year_to"),
        ("floors_from", "floors_to"),
        ("garden_area_from", "garden_area_to"),
        ("building_area_from", "building_area_to"),
        ("pool_area_from", "pool_area_to"),
        ("cellar_area_from", "cellar_area_to"),
        ("garage_area_from", "garage_area_to"),
    )

    EXISTS_AREA_FILTERS: ClassVar[tuple[tuple[str, str, str, str], ...]] = (
        (
            "has_balcony",
            "balcony_area_from",
            "balcony_area_to",
            "balcony_area",
        ),
        ("has_loggia", "loggia_area_from", "loggia_area_to", "loggia_area"),
        (
            "has_terrace",
            "terrace_area_from",
            "terrace_area_to",
            "terrace_area",
        ),
        ("has_garden", "garden_area_from", "garden_area_to", "garden_area"),
        ("has_pool", "pool_area_from", "pool_area_to", "pool_area"),
        ("has_cellar", "cellar_area_from", "cellar_area_to", "cellar_area"),
        ("has_garage", "garage_area_from", "garage_area_to", "garage_area"),
    )

    # pagination
    page: int = Field(default=1, ge=1, le=999_999)
    page_size: int = Field(default=20, ge=1, le=100)

    # sorting
    sort_by: EstateSortBy = EstateSortBy.published_at
    order: SortOrder = SortOrder.desc

    # Estate
    estate_type: list[EstateType] | None = Field(
        default=None,
        min_length=1,
    )
    offer_type: list[OfferType] | None = Field(
        default=None,
        min_length=1,
    )

    created_at_from: datetime.datetime | None = None
    created_at_to: datetime.datetime | None = None

    # EstateLocation
    region: list[Region] | None = Field(
        default=None,
        min_length=1,
    )

    # EstatePricing
    price_from: NonNegativeMoneyAmount | None = None
    price_to: NonNegativeMoneyAmount | None = None

    price_unit: list[PriceUnit] | None = Field(
        default=None,
        min_length=1,
    )

    cost_of_living_from: NonNegativeMoneyAmount | None = None
    cost_of_living_to: NonNegativeMoneyAmount | None = None

    commission_paid_by_owner: bool | None = None

    # EstateListing
    published_at_from: datetime.datetime | None = None
    published_at_to: datetime.datetime | None = None

    expires_at_from: datetime.datetime | None = None
    expires_at_to: datetime.datetime | None = None

    available_from_from: datetime.date | None = None
    available_from_to: datetime.date | None = None

    # EstateUtilities
    has_cold_water: bool | None = None
    has_hot_water: bool | None = None
    has_gas: bool | None = None
    has_sewerage: bool | None = None

    heating_source: list[HeatingSource] | None = Field(
        default=None,
        min_length=1,
    )
    primary_internet_connection_type: (
        list[PrimaryInternetConnectionType] | None
    ) = Field(
        default=None,
        min_length=1,
    )

    # EstateDetails
    condition: list[PropertyCondition] | None = Field(
        default=None,
        min_length=1,
    )
    energy_class: list[EnergyClass] | None = Field(
        default=None,
        min_length=1,
    )
    furnishing: list[Furnishing] | None = Field(
        default=None,
        min_length=1,
    )
    easy_access: bool | None = None

    usable_area_from: NonNegativeArea | None = None
    usable_area_to: NonNegativeArea | None = None

    total_property_area_from: NonNegativeArea | None = None
    total_property_area_to: NonNegativeArea | None = None

    # EstateApartment
    apartment_layout: list[ApartmentLayout] | None = Field(
        default=None,
        min_length=1,
    )

    floor_number_from: int | None = Field(default=None, ge=0, le=200)
    floor_number_to: int | None = Field(default=None, ge=0, le=200)

    has_elevator: bool | None = None

    has_balcony: bool | None = None
    balcony_area_from: PositiveArea | None = None
    balcony_area_to: PositiveArea | None = None

    has_loggia: bool | None = None
    loggia_area_from: PositiveArea | None = None
    loggia_area_to: PositiveArea | None = None

    has_terrace: bool | None = None
    terrace_area_from: PositiveArea | None = None
    terrace_area_to: PositiveArea | None = None

    # EstateHouse
    room_count: list[RoomCount] | None = Field(
        default=None,
        min_length=1,
    )
    house_type: list[HouseType] | None = Field(
        default=None,
        min_length=1,
    )

    acceptance_year_from: AcceptanceYear | None = None
    acceptance_year_to: AcceptanceYear | None = None

    floors_from: int | None = Field(default=None, ge=1)
    floors_to: int | None = Field(default=None, ge=1)

    has_garden: bool | None = None
    garden_area_from: PositiveArea | None = None
    garden_area_to: PositiveArea | None = None

    building_area_from: NonNegativeArea | None = None
    building_area_to: NonNegativeArea | None = None

    has_pool: bool | None = None
    pool_area_from: PositiveArea | None = None
    pool_area_to: PositiveArea | None = None

    has_cellar: bool | None = None
    cellar_area_from: PositiveArea | None = None
    cellar_area_to: PositiveArea | None = None

    has_garage: bool | None = None
    garage_area_from: PositiveArea | None = None
    garage_area_to: PositiveArea | None = None

    # EstateVicinity
    vicinity_type: list[VicinityType] | None = Field(
        default=None,
        min_length=1,
    )
    vicinity_distance_m_to: int | None = Field(default=None, ge=0, le=100_000)

    @model_validator(mode="after")
    def validate_filter_ranges(self):
        errors: list[InitErrorDetails] = []

        for from_field, to_field in self.RANGE_FILTERS:
            self._validate_range(errors, from_field, to_field)

        for (
            exists_field,
            from_field,
            to_field,
            area_name,
        ) in self.EXISTS_AREA_FILTERS:
            self._validate_exists_filter(
                errors=errors,
                exists_field=exists_field,
                from_field=from_field,
                to_field=to_field,
                area_name=area_name,
            )

        if errors:
            raise ValidationError.from_exception_data(
                title=type(self).__name__,
                line_errors=errors,
            )

        return self

    def _validate_range(
        self,
        errors: list[InitErrorDetails],
        from_field: str,
        to_field: str,
    ) -> None:
        from_value = getattr(self, from_field)
        to_value = getattr(self, to_field)

        if from_value is None or to_value is None:
            return

        if from_value <= to_value:
            return

        errors.append(
            make_value_error(
                loc=(from_field,),
                message=f"{from_field} cannot be greater than {to_field}",
                input_value=from_value,
            )
        )

    def _validate_exists_filter(
        self,
        errors: list[InitErrorDetails],
        exists_field: str,
        from_field: str,
        to_field: str,
        area_name: str,
    ) -> None:
        exists_value = getattr(self, exists_field)
        from_value = getattr(self, from_field)
        to_value = getattr(self, to_field)

        if exists_value is not False:
            return

        if from_value is None and to_value is None:
            return

        errors.append(
            make_value_error(
                loc=(exists_field,),
                message=(
                    f"{area_name} range cannot be used "
                    f"when {exists_field}=false"
                ),
                input_value=exists_value,
            )
        )


class EstatePublicFilterRequest(EstateBaseFilterRequest):
    agent_id: uuid.UUID | None = None
    saved_by_current_user: bool | None = None


class EstateAdminFilterRequest(EstatePublicFilterRequest):
    seller_id: uuid.UUID | None = None
    status: list[ListingStatus] | None = Field(
        default=None,
        min_length=1,
    )


class EstateAgentOwnFilterRequest(EstateBaseFilterRequest):
    status: list[ListingStatus] | None = Field(
        default=None,
        min_length=1,
    )
