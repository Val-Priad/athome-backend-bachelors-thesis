import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey
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
    condition: Mapped[PropertyCondition | None] = mapped_column(
        Enum(PropertyCondition, name="property_condition_enum"),
    )
    energy_class: Mapped[EnergyClass | None] = mapped_column(
        Enum(EnergyClass, name="energy_class_enum"),
    )
    usable_area: Mapped[float] = mapped_column(Float)
    total_property_area: Mapped[float | None] = mapped_column(Float)
    furnishing: Mapped[Furnishing | None] = mapped_column(
        Enum(Furnishing, name="furnishing_enum"),
    )
    easy_access: Mapped[bool | None] = mapped_column(Boolean)

    estate: Mapped["Estate"] = relationship("Estate", back_populates="details")
