from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from domain.estate.models.estate_media_model import EstateMedia


class EstateMediaRepository:
    def object_key_exists(
        self,
        session: Session,
        object_key: str,
    ) -> bool:
        return session.execute(
            select(exists().where(EstateMedia.object_key == object_key))
        ).scalar_one()

    def get_used_object_keys(
        self,
        session: Session,
        object_keys: list[str],
    ) -> set[str]:
        if not object_keys:
            return set()

        return set(
            session.scalars(
                select(EstateMedia.object_key).where(
                    EstateMedia.object_key.in_(object_keys)
                )
            )
        )
