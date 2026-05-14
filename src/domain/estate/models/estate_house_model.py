import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.house_enums import HouseType, RoomCount
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate


class EstateHouse(Base):
    __tablename__ = "estate_houses"

    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    room_count: Mapped[RoomCount | None] = mapped_column(
        Enum(RoomCount, name="room_count_enum"),
        nullable=True,
    )
    house_type: Mapped[HouseType | None] = mapped_column(
        Enum(HouseType, name="house_type_enum"),
        nullable=True,
    )
    acceptance_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    floors: Mapped[int | None] = mapped_column(Integer, nullable=True)
    underground_floors: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    parking_lots_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    garden_area: Mapped[float | None] = mapped_column(Float, nullable=True)
    building_area: Mapped[float | None] = mapped_column(Float, nullable=True)
    pool_area: Mapped[float | None] = mapped_column(Float, nullable=True)
    cellar_area: Mapped[float | None] = mapped_column(Float, nullable=True)
    garage_area: Mapped[float | None] = mapped_column(Float, nullable=True)

    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="house",
    )
