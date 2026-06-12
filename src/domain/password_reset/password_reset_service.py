import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from domain.password_reset.password_reset_repository import (
    PasswordResetRepository,
)
from domain.token.token_lifecycle_service import TokenLifecycleService
from exceptions.custom_exceptions.mailer_exceptions import EmailSendError
from infrastructure.email.mailer_protocol import MailerProtocol
from security import PasswordCrypto, TokenCrypto


class PasswordResetService:
    def __init__(
        self,
        password_reset_repository: PasswordResetRepository,
        mailer: MailerProtocol,
        token_hasher: TokenCrypto,
        password_hasher: PasswordCrypto,
        token_lifecycle_service: TokenLifecycleService,
    ):
        self.password_reset_repository = password_reset_repository
        self.mailer = mailer
        self.token_hasher = token_hasher
        self.password_hasher = password_hasher
        self.token_lifecycle_service = token_lifecycle_service

    TOKEN_TTL = timedelta(minutes=10)

    def send_reset_password_email(self, email_to: str, token: str):
        try:
            return self.mailer.send_reset_password_email(email_to, token)
        except Exception:
            raise EmailSendError()

    def get_token(
        self,
        session: Session,
        user_id: uuid.UUID,
    ):
        return self.token_lifecycle_service.create_token(
            session,
            user_id,
            token_crypto=self.token_hasher,
            repository=self.password_reset_repository,
            ttl=self.TOKEN_TTL,
        )

    def reset_password(self, session: Session, raw_token: str, password: str):
        token = self.password_reset_repository.get_valid_token(
            session, self.token_hasher.hash_token(raw_token)
        )

        token.used_at = datetime.now(timezone.utc)
        token.user.password_hash = self.password_hasher.hash_password(password)

        self.password_reset_repository.deactivate_all_user_tokens(
            session, token.user.id
        )
