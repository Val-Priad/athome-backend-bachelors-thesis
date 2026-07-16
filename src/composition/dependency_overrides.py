from dataclasses import dataclass

from application.ports import (
    MailerProtocol,
    ObjectStorageProtocol,
    VicinityClientProtocol,
)
from application.ports.transaction_manager import SessionFactory


@dataclass(frozen=True, slots=True)
class DependencyOverrides:
    mailer: MailerProtocol | None = None
    object_storage: ObjectStorageProtocol | None = None
    vicinity_client: VicinityClientProtocol | None = None
    session_factory: SessionFactory | None = None
