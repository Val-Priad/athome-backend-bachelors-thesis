import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_details_enums import (
    EnergyClass,
    Furnishing,
    PropertyCondition,
)
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateDetails(Base):
    __tablename__ = "estate_details"

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    condition: Mapped[PropertyCondition] = mapped_column(
        Enum(PropertyCondition, name="property_condition_enum"),
        nullable=False,
    )
    energy_class: Mapped[EnergyClass] = mapped_column(
        Enum(EnergyClass, name="energy_class_enum"),
        nullable=False,
    )
    usable_area: Mapped[float] = mapped_column(Float, nullable=False)
    total_area: Mapped[float | None] = mapped_column(Float, nullable=True)

    furnishing: Mapped[Furnishing] = mapped_column(
        Enum(Furnishing, name="furnishing_enum"),
        nullable=False,
    )
    easy_access: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    estate: Mapped["Estate"] = relationship("Estate", back_populates="details")
