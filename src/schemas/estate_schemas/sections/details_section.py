from domain.estate.enums.estate_details_enums import (
    EnergyClass,
    Furnishing,
    PropertyCondition,
)
from schemas.parent_types import RequestValidation
from schemas.types import NonNegativeArea, PositiveArea


class EstateDetailsSection(RequestValidation):
    condition: PropertyCondition | None = None
    energy_class: EnergyClass | None = None

    usable_area: PositiveArea
    total_property_area: NonNegativeArea | None = None

    furnishing: Furnishing | None = None
    easy_access: bool | None = None
