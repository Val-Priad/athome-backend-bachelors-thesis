from domain.estate.enums.utilities_enums import (
    HeatingSource,
    PrimaryInternetConnectionType,
)
from schemas.parent_types import RequestValidation


class EstateUtilitiesSection(RequestValidation):
    has_cold_water: bool | None = None
    has_hot_water: bool | None = None
    has_gas: bool | None = None
    has_sewerage: bool | None = None

    heating_source: HeatingSource | None = None
    primary_internet_connection_type: PrimaryInternetConnectionType | None = (
        None
    )
