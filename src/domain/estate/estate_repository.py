from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from domain.estate.estate_model import Estate
from exceptions.custom_exceptions.estate_exceptions import EstateNotFoundError


class EstateRepository:
    def add(self, session: Session, estate: Estate) -> Estate:
        session.add(estate)
        session.flush()
        return estate

    def get_estate_full_by_id(
        self,
        session: Session,
        estate_id: UUID,
    ) -> Estate:
        stmt = (
            select(Estate)
            .where(Estate.id == estate_id)
            .options(
                joinedload(Estate.seller),
                joinedload(Estate.agent),
                joinedload(Estate.location),
                joinedload(Estate.pricing),
                joinedload(Estate.listing),
                joinedload(Estate.utilities),
                joinedload(Estate.details),
                joinedload(Estate.apartment),
                joinedload(Estate.house),
                selectinload(Estate.translations),
                selectinload(Estate.media),
                selectinload(Estate.vicinities),
            )
        )

        estate = session.scalar(stmt)

        if estate is None:
            raise EstateNotFoundError()

        return estate
