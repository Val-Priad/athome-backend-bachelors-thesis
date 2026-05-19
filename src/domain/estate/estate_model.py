import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.models.estate_apartment_model import EstateApartment
from domain.estate.models.estate_details_model import EstateDetails
from domain.estate.models.estate_house_model import EstateHouse
from domain.estate.models.estate_listing_model import EstateListing
from domain.estate.models.estate_location_model import EstateLocation
from domain.estate.models.estate_media_model import EstateMedia
from domain.estate.models.estate_pricing_model import EstatePricing
from domain.estate.models.estate_translation_model import EstateTranslation
from domain.estate.models.estate_utilities_model import EstateUtilities
from domain.estate.models.estate_vicinity_model import EstateVicinity
from domain.estate.models.saved_estate_model import SavedEstate
from infrastructure.db import Base

if TYPE_CHECKING:
    from domain.user.user_model import User


class Estate(Base):
    __tablename__ = "estates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    seller_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    broker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    estate_type: Mapped[EstateType] = mapped_column(
        Enum(EstateType, name="estate_type_enum"), nullable=False
    )
    offer_type: Mapped[OfferType] = mapped_column(
        Enum(OfferType, name="offer_type_enum"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    seller: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[seller_id],
        back_populates="owned_estates",
    )
    broker: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[broker_id],
        back_populates="brokered_estates",
    )
    location: Mapped["EstateLocation | None"] = relationship(
        "EstateLocation",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )
    pricing: Mapped["EstatePricing | None"] = relationship(
        "EstatePricing",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )
    listing: Mapped["EstateListing | None"] = relationship(
        "EstateListing",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )
    utilities: Mapped["EstateUtilities | None"] = relationship(
        "EstateUtilities",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )
    details: Mapped["EstateDetails | None"] = relationship(
        "EstateDetails",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )
    apartment: Mapped["EstateApartment | None"] = relationship(
        "EstateApartment",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )
    house: Mapped["EstateHouse | None"] = relationship(
        "EstateHouse",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )
    translations: Mapped[list["EstateTranslation"]] = relationship(
        "EstateTranslation",
        back_populates="estate",
        cascade="all, delete-orphan",
    )
    media: Mapped[list["EstateMedia"]] = relationship(
        "EstateMedia",
        back_populates="estate",
        cascade="all, delete-orphan",
    )
    vicinities: Mapped[list["EstateVicinity"]] = relationship(
        "EstateVicinity",
        back_populates="estate",
        cascade="all, delete-orphan",
    )
    saved_by_users: Mapped[list["SavedEstate"]] = relationship(
        "SavedEstate",
        back_populates="estate",
        cascade="all, delete-orphan",
    )
