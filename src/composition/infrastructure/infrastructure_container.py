from dataclasses import dataclass

from application.transactions import TransactionManagerProtocol
from infrastructure.email.mailer_protocol import MailerProtocol
from infrastructure.object_storage.object_storage_protocol import (
    ObjectStorageProtocol,
)
from infrastructure.vicinity.vicinity_protocol import VicinityClientProtocol
from security.password_crypto import PasswordCrypto
from security.token_crypto import TokenCrypto


@dataclass(frozen=True, slots=True)
class ApplicationUrls:
    app_base_url: str
    media_base_url: str


@dataclass(frozen=True, slots=True)
class InfrastructureContainer:
    transactions: TransactionManagerProtocol
    mailer: MailerProtocol
    object_storage: ObjectStorageProtocol
    vicinity_client: VicinityClientProtocol
    password_hasher: PasswordCrypto
    token_hasher: TokenCrypto
    urls: ApplicationUrls
