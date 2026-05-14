import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.apartment_enums import ApartmentLayout
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateApartment(Base):
    __tablename__ = "estate_apartments"

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    apartment_layout: Mapped[ApartmentLayout | None] = mapped_column(
        Enum(ApartmentLayout, name="apartment_layout_enum"),
        nullable=True,
    )
    floor_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_elevator: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    balcony_area: Mapped[float | None] = mapped_column(Float, nullable=True)
    loggia_area: Mapped[float | None] = mapped_column(Float, nullable=True)
    terrace_area: Mapped[float | None] = mapped_column(Float, nullable=True)

    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="apartment",
    )
