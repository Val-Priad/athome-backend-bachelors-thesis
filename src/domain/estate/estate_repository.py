from sqlalchemy.orm import Session

from domain.estate.estate_model import Estate


class EstateRepository:
    def add(self, session: Session, estate: Estate) -> None:
        session.add(estate)
