from dataclasses import dataclass

from application.ports import (
    MailerProtocol,
    ObjectStorageProtocol,
    VicinityClientProtocol,
)
from application.ports.transaction_manager import TransactionManagerProtocol
from configuration.application_urls import ApplicationUrls
from security.password_crypto import PasswordCrypto
from security.token_crypto import TokenCrypto


@dataclass(frozen=True, slots=True)
class InfrastructureContainer:
    transactions: TransactionManagerProtocol
    mailer: MailerProtocol
    object_storage: ObjectStorageProtocol
    vicinity_client: VicinityClientProtocol
    password_hasher: PasswordCrypto
    token_hasher: TokenCrypto
    urls: ApplicationUrls
