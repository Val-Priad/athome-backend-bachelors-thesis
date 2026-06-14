import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_location_enums import Region
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateLocation(Base):
    __tablename__ = "estate_locations"

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    region: Mapped[Region] = mapped_column(Enum(Region, name="region_enum"))
    city: Mapped[str] = mapped_column(String(255))
    street: Mapped[str] = mapped_column(String(255))
    house_number: Mapped[str | None] = mapped_column(String(50))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    estate: Mapped["Estate"] = relationship(
        "Estate", back_populates="location"
    )
