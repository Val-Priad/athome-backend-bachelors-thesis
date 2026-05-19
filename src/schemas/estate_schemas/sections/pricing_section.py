from decimal import Decimal

from pydantic import Field

from domain.estate.enums.estate_pricing_enums import PriceUnit
from schemas.parent_types import RequestValidation


class EstatePricingSection(RequestValidation):
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
