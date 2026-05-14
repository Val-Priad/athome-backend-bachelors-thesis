import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, text
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
    apartment_layout: Mapped[ApartmentLayout] = mapped_column(
        Enum(ApartmentLayout, name="apartment_layout_enum"),
        nullable=False,
    )
    floor_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_elevator: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    balcony_area: Mapped[float] = mapped_column(Float, nullable=False)
    loggia_area: Mapped[float] = mapped_column(Float, nullable=False)
    terrace_area: Mapped[float] = mapped_column(Float, nullable=False)

    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="apartment",
    )
