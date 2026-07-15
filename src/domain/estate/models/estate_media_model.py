import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_media_enums import MediaType
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateMedia(Base):
    __tablename__ = "estate_media"

    __table_args__ = (
        CheckConstraint(
            "position >= 0",
            name="ck_estate_media_position_non_negative",
        ),
        UniqueConstraint(
            "estate_id",
            "position",
            name="uq_estate_media_estate_position",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
    )
    object_key: Mapped[str] = mapped_column(Text, unique=True)
    media_type: Mapped[MediaType] = mapped_column(
        Enum(MediaType, name="media_type_enum"),
    )
    alt: Mapped[str | None] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="media",
    )
