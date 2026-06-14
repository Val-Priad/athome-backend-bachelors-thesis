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
    )
    house_type: Mapped[HouseType] = mapped_column(
        Enum(HouseType, name="house_type_enum"),
    )
    acceptance_year: Mapped[int | None] = mapped_column(Integer)
    floors: Mapped[int] = mapped_column(Integer)
    underground_floors: Mapped[int | None] = mapped_column(Integer)
    parking_lots_count: Mapped[int | None] = mapped_column(Integer)
    garden_area: Mapped[float | None] = mapped_column(Float)
    building_area: Mapped[float | None] = mapped_column(Float)
    pool_area: Mapped[float | None] = mapped_column(Float)
    cellar_area: Mapped[float | None] = mapped_column(Float)
    garage_area: Mapped[float | None] = mapped_column(Float)

    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="house",
    )
