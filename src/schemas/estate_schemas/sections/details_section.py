from pydantic import Field

from domain.estate.enums.estate_details_enums import (
    EnergyClass,
    Furnishing,
    PropertyCondition,
)
from schemas.parent_types import RequestValidation


class EstateDetailsSection(RequestValidation):
    condition: PropertyCondition | None = None
    energy_class: EnergyClass | None = None

    usable_area: float = Field(gt=0)
    total_property_area: float | None = Field(default=None, ge=0)

    furnishing: Furnishing | None = None
    easy_access: bool | None = None
