from dataclasses import dataclass

from application.ports import (
    MailerProtocol,
    ObjectStorageProtocol,
    VicinityClientProtocol,
)
from application.ports.transaction_manager import TransactionManagerProtocol
from configuration.application_urls import ApplicationUrls


@dataclass(frozen=True, slots=True)
class InfrastructureContainer:
    transactions: TransactionManagerProtocol
    mailer: MailerProtocol
    object_storage: ObjectStorageProtocol
    vicinity_client: VicinityClientProtocol
    urls: ApplicationUrls
