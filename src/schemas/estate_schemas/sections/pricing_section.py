from domain.estate.enums.estate_pricing_enums import PriceUnit
from schemas.parent_types import RequestValidation
from schemas.types import NonNegativeMoneyAmount, PositiveMoneyAmount


class EstatePricingSection(RequestValidation):
    price: PositiveMoneyAmount
    price_unit: PriceUnit

    cost_of_living: NonNegativeMoneyAmount | None = None
    commission: NonNegativeMoneyAmount | None = None
    commission_paid_by_owner: bool | None = None

    refundable_deposit: NonNegativeMoneyAmount | None = None
