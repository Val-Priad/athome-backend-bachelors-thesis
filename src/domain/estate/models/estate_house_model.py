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
    room_count: Mapped[RoomCount] = mapped_column(
        Enum(RoomCount, name="room_count_enum"),
        nullable=False,
    )
    house_type: Mapped[HouseType] = mapped_column(
        Enum(HouseType, name="house_type_enum"),
        nullable=False,
    )
    acceptance_year: Mapped[int] = mapped_column(Integer, nullable=False)
    floors: Mapped[int] = mapped_column(Integer, nullable=False)
    underground_floors: Mapped[int] = mapped_column(Integer, nullable=False)
    parking_lots_count: Mapped[int] = mapped_column(Integer, nullable=False)
    garden_area: Mapped[float] = mapped_column(Float, nullable=False)
    building_area: Mapped[float | None] = mapped_column(Float, nullable=True)
    pool_area: Mapped[float] = mapped_column(Float, nullable=False)
    cellar_area: Mapped[float] = mapped_column(Float, nullable=False)
    garage_area: Mapped[float] = mapped_column(Float, nullable=False)

    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="house",
    )
