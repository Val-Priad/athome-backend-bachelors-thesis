import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from application.ports.mailer import MailerProtocol
from domain.email_verification.email_verification_repository import (
    EmailVerificationRepository,
)
from domain.token.token_lifecycle_service import TokenLifecycleService
from domain.user.user_model import User
from exceptions.custom_exceptions.mailer_exceptions import EmailSendError
from exceptions.custom_exceptions.user_exceptions import (
    TokenVerificationError,
    UserAlreadyVerifiedError,
)
from security import TokenCrypto


class EmailVerificationService:
    def __init__(
        self,
        email_verification_repository: EmailVerificationRepository,
        mailer: MailerProtocol,
        token_hasher: TokenCrypto,
        token_lifecycle_service: TokenLifecycleService,
    ):
        self.email_verification_repository = email_verification_repository
        self.mailer = mailer
        self.token_hasher = token_hasher
        self.token_lifecycle_service = token_lifecycle_service

    TOKEN_TTL = timedelta(hours=24)

    def send_verification_email(self, email_to: str, token: str):
        try:
            return self.mailer.send_verification_email(email_to, token)
        except Exception:
            raise EmailSendError()

    @staticmethod
    def ensure_user_is_not_verified(user: User) -> None:
        if user.is_email_verified:
            raise UserAlreadyVerifiedError()

    def create_token(
        self,
        session: Session,
        user_id: uuid.UUID,
    ):
        return self.token_lifecycle_service.create_token(
            session,
            user_id,
            token_crypto=self.token_hasher,
            repository=self.email_verification_repository,
            ttl=self.TOKEN_TTL,
        )

    def get_resend_token(self, session: Session, user_id: uuid.UUID):
        return self.create_token(session, user_id)

    def verify_token(self, session: Session, raw_token: str) -> None:
        token = self.email_verification_repository.find_by_hash(
            session,
            self.token_hasher.hash_token(raw_token),
        )

        if token is None:
            raise TokenVerificationError(
                "The email verification token is invalid, expired, or already used"
            )

        now = datetime.now(timezone.utc)

        if token.user.is_email_verified:
            return

        if token.used_at is not None:
            raise TokenVerificationError(
                "The email verification token is invalid, expired, or already used"
            )

        if token.expires_at <= now:
            if token.user.is_email_verified:
                return

            raise TokenVerificationError(
                "The email verification token is expired"
            )

        token.used_at = now
        token.user.is_email_verified = True

        self.email_verification_repository.deactivate_all_user_tokens(
            session,
            token.user.id,
        )
