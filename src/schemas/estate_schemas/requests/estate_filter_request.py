import datetime
import uuid
from decimal import Decimal
from enum import Enum
from typing import Annotated, ClassVar

from pydantic import (
    BaseModel,
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


class EstatePublicFilterRequest(BaseModel):
    current_year: ClassVar[int] = datetime.date.today().year

    model_config = ConfigDict(extra="forbid")

    # pagination
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=100)] = 20

    # sorting
    sort_by: EstateSortBy = EstateSortBy.published_at
    order: SortOrder = SortOrder.desc

    # Estate
    agent_id: uuid.UUID | None = None

    estate_type: Annotated[list[EstateType] | None, Field(min_length=1)] = None
    offer_type: Annotated[list[OfferType] | None, Field(min_length=1)] = None

    created_at_from: datetime.datetime | None = None
    created_at_to: datetime.datetime | None = None

    # saved_by_users
    saved_by_current_user: bool | None = None

    # EstateLocation
    region: Annotated[list[Region] | None, Field(min_length=1)] = None

    # EstatePricing
    price_from: Annotated[Decimal | None, Field(ge=0)] = None
    price_to: Annotated[Decimal | None, Field(ge=0)] = None

    price_unit: Annotated[list[PriceUnit] | None, Field(min_length=1)] = None

    cost_of_living_from: Annotated[Decimal | None, Field(ge=0)] = None
    cost_of_living_to: Annotated[Decimal | None, Field(ge=0)] = None

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

    heating_source: Annotated[
        list[HeatingSource] | None, Field(min_length=1)
    ] = None
    primary_internet_connection_type: Annotated[
        list[PrimaryInternetConnectionType] | None, Field(min_length=1)
    ] = None

    # EstateDetails
    condition: Annotated[
        list[PropertyCondition] | None, Field(min_length=1)
    ] = None
    energy_class: Annotated[list[EnergyClass] | None, Field(min_length=1)] = (
        None
    )
    furnishing: Annotated[list[Furnishing] | None, Field(min_length=1)] = None
    easy_access: bool | None = None

    usable_area_from: Annotated[float | None, Field(gt=0)] = None
    usable_area_to: Annotated[float | None, Field(gt=0)] = None

    total_property_area_from: Annotated[float | None, Field(gt=0)] = None
    total_property_area_to: Annotated[float | None, Field(gt=0)] = None

    # EstateApartment
    apartment_layout: Annotated[
        list[ApartmentLayout] | None, Field(min_length=1)
    ] = None

    floor_number_from: Annotated[int | None, Field(ge=-5, le=200)] = None
    floor_number_to: Annotated[int | None, Field(ge=-5, le=200)] = None

    has_elevator: bool | None = None

    has_balcony: bool | None = None
    balcony_area_from: Annotated[float | None, Field(gt=0)] = None
    balcony_area_to: Annotated[float | None, Field(gt=0)] = None

    has_loggia: bool | None = None
    loggia_area_from: Annotated[float | None, Field(gt=0)] = None
    loggia_area_to: Annotated[float | None, Field(gt=0)] = None

    has_terrace: bool | None = None
    terrace_area_from: Annotated[float | None, Field(gt=0)] = None
    terrace_area_to: Annotated[float | None, Field(gt=0)] = None

    # EstateHouse
    room_count: Annotated[list[RoomCount] | None, Field(min_length=1)] = None
    house_type: Annotated[list[HouseType] | None, Field(min_length=1)] = None

    acceptance_year_from: Annotated[
        int | None, Field(ge=1800, le=current_year + 10)
    ] = None
    acceptance_year_to: Annotated[
        int | None, Field(ge=1800, le=current_year + 10)
    ] = None

    floors_from: Annotated[int | None, Field(ge=1)] = None
    floors_to: Annotated[int | None, Field(ge=1)] = None

    has_garden: bool | None = None
    garden_area_from: Annotated[float | None, Field(gt=0)] = None
    garden_area_to: Annotated[float | None, Field(gt=0)] = None

    building_area_from: Annotated[float | None, Field(gt=0)] = None
    building_area_to: Annotated[float | None, Field(gt=0)] = None

    has_pool: bool | None = None
    pool_area_from: Annotated[float | None, Field(gt=0)] = None
    pool_area_to: Annotated[float | None, Field(gt=0)] = None

    has_cellar: bool | None = None
    cellar_area_from: Annotated[float | None, Field(gt=0)] = None
    cellar_area_to: Annotated[float | None, Field(gt=0)] = None

    has_garage: bool | None = None
    garage_area_from: Annotated[float | None, Field(gt=0)] = None
    garage_area_to: Annotated[float | None, Field(gt=0)] = None

    # EstateVicinity
    vicinity_type: Annotated[
        list[VicinityType] | None, Field(min_length=1)
    ] = None
    vicinity_distance_m_to: Annotated[int | None, Field(gt=0)] = None

    @model_validator(mode="after")
    def validate_filter_ranges(self):
        errors: list[InitErrorDetails] = []

        self._validate_range(errors, "created_at_from", "created_at_to")
        self._validate_range(errors, "price_from", "price_to")
        self._validate_range(
            errors, "cost_of_living_from", "cost_of_living_to"
        )
        self._validate_range(errors, "published_at_from", "published_at_to")
        self._validate_range(errors, "expires_at_from", "expires_at_to")
        self._validate_range(
            errors, "available_from_from", "available_from_to"
        )

        self._validate_range(errors, "usable_area_from", "usable_area_to")
        self._validate_range(
            errors,
            "total_property_area_from",
            "total_property_area_to",
        )

        self._validate_range(errors, "floor_number_from", "floor_number_to")
        self._validate_range(errors, "balcony_area_from", "balcony_area_to")
        self._validate_range(errors, "loggia_area_from", "loggia_area_to")
        self._validate_range(errors, "terrace_area_from", "terrace_area_to")

        self._validate_range(
            errors, "acceptance_year_from", "acceptance_year_to"
        )
        self._validate_range(errors, "floors_from", "floors_to")
        self._validate_range(errors, "garden_area_from", "garden_area_to")
        self._validate_range(errors, "building_area_from", "building_area_to")
        self._validate_range(errors, "pool_area_from", "pool_area_to")
        self._validate_range(errors, "cellar_area_from", "cellar_area_to")
        self._validate_range(errors, "garage_area_from", "garage_area_to")

        self._validate_exists_filter(
            errors=errors,
            exists_field="has_balcony",
            from_field="balcony_area_from",
            to_field="balcony_area_to",
            area_name="balcony_area",
        )
        self._validate_exists_filter(
            errors=errors,
            exists_field="has_loggia",
            from_field="loggia_area_from",
            to_field="loggia_area_to",
            area_name="loggia_area",
        )
        self._validate_exists_filter(
            errors=errors,
            exists_field="has_terrace",
            from_field="terrace_area_from",
            to_field="terrace_area_to",
            area_name="terrace_area",
        )
        self._validate_exists_filter(
            errors=errors,
            exists_field="has_garden",
            from_field="garden_area_from",
            to_field="garden_area_to",
            area_name="garden_area",
        )
        self._validate_exists_filter(
            errors=errors,
            exists_field="has_pool",
            from_field="pool_area_from",
            to_field="pool_area_to",
            area_name="pool_area",
        )
        self._validate_exists_filter(
            errors=errors,
            exists_field="has_cellar",
            from_field="cellar_area_from",
            to_field="cellar_area_to",
            area_name="cellar_area",
        )
        self._validate_exists_filter(
            errors=errors,
            exists_field="has_garage",
            from_field="garage_area_from",
            to_field="garage_area_to",
            area_name="garage_area",
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


class EstateAdminFilterRequest(EstatePublicFilterRequest):
    # Estate
    seller_id: uuid.UUID | None = None

    # EstateListing
    status: Annotated[list[ListingStatus] | None, Field(min_length=1)] = None
