import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from domain.password_reset.password_reset_model import PasswordReset
from exceptions.custom_exceptions.user_exceptions import TokenVerificationError


class PasswordResetRepository:
    def deactivate_all_user_tokens(
        self, session: Session, user_id: uuid.UUID
    ) -> None:
        session.execute(
            update(PasswordReset)
            .where(
                PasswordReset.user_id == user_id,
                PasswordReset.used_at.is_(None),
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
            PasswordReset(
                user_id=user_id, token_hash=hashed_token, expires_at=expires_at
            )
        )

    def get_valid_token(
        self, session: Session, hashed_token: bytes
    ) -> PasswordReset:
        token = session.scalar(
            select(PasswordReset).where(
                PasswordReset.token_hash == hashed_token,
                PasswordReset.used_at.is_(None),
                PasswordReset.expires_at > datetime.now(timezone.utc),
            )
        )
        if token is None:
            raise TokenVerificationError(
                "The password reset token is invalid, expired, or already used"
            )
        return token
