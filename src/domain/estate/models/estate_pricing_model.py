import uuid
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_pricing_enums import PriceUnit
from infrastructure.db import Base


class EstatePricing(Base):
    __tablename__ = "estate_pricings"

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    price_unit: Mapped[PriceUnit | None] = mapped_column(
        Enum(PriceUnit, name="price_unit_enum"), nullable=True
    )

    cost_of_living: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    commission: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    commission_paid_by_owner: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    refundable_deposit: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    estate = relationship("Estate", back_populates="pricing")
