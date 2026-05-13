import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_listing_enums import ListingStatus
from infrastructure.db import Base


class EstateListing(Base):
    __tablename__ = "estate_listing"

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )

    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status_enum"),
        nullable=False,
        default=ListingStatus.draft,
        server_default=ListingStatus.draft.value,
    )
    # TODO: When listing is published for the first time,
    # set published_at and expires_at in service layer.
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)

    estate = relationship("Estate", back_populates="listing")
