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

    _CASCADE_ALL_DELETE_ORPHAN = "all, delete-orphan"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    seller_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    estate_type: Mapped[EstateType] = mapped_column(
        Enum(EstateType, name="estate_type_enum")
    )
    offer_type: Mapped[OfferType] = mapped_column(
        Enum(OfferType, name="offer_type_enum")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    seller: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[seller_id],
        back_populates="owned_estates",
    )
    agent: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[agent_id],
        back_populates="agent_estates",
    )
    location: Mapped["EstateLocation"] = relationship(
        "EstateLocation",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    pricing: Mapped["EstatePricing"] = relationship(
        "EstatePricing",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    listing: Mapped["EstateListing"] = relationship(
        "EstateListing",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    utilities: Mapped["EstateUtilities"] = relationship(
        "EstateUtilities",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    details: Mapped["EstateDetails"] = relationship(
        "EstateDetails",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    apartment: Mapped["EstateApartment | None"] = relationship(
        "EstateApartment",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    house: Mapped["EstateHouse | None"] = relationship(
        "EstateHouse",
        back_populates="estate",
        uselist=False,
        single_parent=True,
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    translations: Mapped[list["EstateTranslation"]] = relationship(
        "EstateTranslation",
        back_populates="estate",
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    media: Mapped[list["EstateMedia"]] = relationship(
        "EstateMedia",
        back_populates="estate",
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
        order_by=EstateMedia.position.asc(),
    )
    vicinities: Mapped[list["EstateVicinity"]] = relationship(
        "EstateVicinity",
        back_populates="estate",
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
    saved_by_users: Mapped[list["SavedEstate"]] = relationship(
        "SavedEstate",
        back_populates="estate",
        cascade=_CASCADE_ALL_DELETE_ORPHAN,
    )
