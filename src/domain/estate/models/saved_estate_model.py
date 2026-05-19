import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.estate.estate_model import Estate
    from domain.user.user_model import User

# TODO: Implement saving liked estate by user


class SavedEstate(Base):
    __tablename__ = "saved_estates"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    estate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("estates.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="saved_estates",
    )
    estate: Mapped["Estate"] = relationship(
        "Estate",
        back_populates="saved_by_users",
    )
