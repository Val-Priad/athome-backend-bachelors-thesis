import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_listing_enums import ListingStatus
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateListing(Base):
    __tablename__ = "estate_listings"

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status_enum"),
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)

    estate: Mapped["Estate"] = relationship("Estate", back_populates="listing")
