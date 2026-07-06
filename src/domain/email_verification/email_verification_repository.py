import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from domain.email_verification.email_verification_model import (
    EmailVerification,
)


class EmailVerificationRepository:
    def deactivate_all_user_tokens(
        self, session: Session, user_id: uuid.UUID
    ) -> None:
        session.execute(
            update(EmailVerification)
            .where(
                EmailVerification.user_id == user_id,
                EmailVerification.used_at.is_(None),
            )
            .values(expires_at=datetime.now(timezone.utc))
        )

    def add_token(
        self,
        session: Session,
        user_id: uuid.UUID,
        hashed_token: bytes,
        expires_at: datetime,
    ) -> None:
        session.add(
            EmailVerification(
                user_id=user_id, token_hash=hashed_token, expires_at=expires_at
            )
        )

    def find_by_hash(
        self, session: Session, hashed_token: bytes
    ) -> EmailVerification | None:
        return session.scalar(
            select(EmailVerification).where(
                EmailVerification.token_hash == hashed_token,
            )
        )
