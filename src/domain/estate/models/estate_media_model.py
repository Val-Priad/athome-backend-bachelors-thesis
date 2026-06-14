import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_media_enums import MediaType
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateMedia(Base):
    __tablename__ = "estate_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("estates.id", ondelete="CASCADE")
    )

    url: Mapped[str] = mapped_column(Text)
    media_type: Mapped[MediaType] = mapped_column(
        Enum(MediaType, name="media_type_enum")
    )
    alt: Mapped[str | None] = mapped_column(String(255))
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="media",
    )
