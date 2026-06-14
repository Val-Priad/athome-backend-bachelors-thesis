import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_vicinity_enums import VicinityType
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateVicinity(Base):
    __tablename__ = "estate_vicinities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("estates.id", ondelete="CASCADE")
    )

    type: Mapped[VicinityType] = mapped_column(
        Enum(VicinityType, name="vicinity_type_enum")
    )
    name: Mapped[str] = mapped_column(String(255))

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    distance_m: Mapped[int] = mapped_column(Integer)

    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="vicinities",
    )
