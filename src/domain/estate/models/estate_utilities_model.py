import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.utilities_enums import (
    HeatingSource,
    PrimaryInternetConnectionType,
)
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateUtilities(Base):
    __tablename__ = "estate_utilities"

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )

    has_cold_water: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    has_hot_water: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    has_gas: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    has_sewerage: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    has_internet: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    # TODO: primary_internet_connection can not be set without has_internet true
    heating_source: Mapped[HeatingSource | None] = mapped_column(
        Enum(HeatingSource, name="heating_source_enum"), nullable=True
    )
    primary_internet_connection_type: Mapped[
        PrimaryInternetConnectionType | None
    ] = mapped_column(
        Enum(
            PrimaryInternetConnectionType,
            name="primary_internet_connection_type_enum",
        ),
        nullable=True,
    )

    estate: Mapped["Estate"] = relationship(
        "Estate", back_populates="utilities"
    )
