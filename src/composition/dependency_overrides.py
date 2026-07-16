from dataclasses import dataclass

from application.transactions import SessionFactory
from infrastructure.email.mailer_protocol import MailerProtocol
from infrastructure.object_storage.object_storage_protocol import (
    ObjectStorageProtocol,
)
from infrastructure.vicinity.vicinity_protocol import VicinityClientProtocol


@dataclass(frozen=True, slots=True)
class DependencyOverrides:
    mailer: MailerProtocol | None = None
    object_storage: ObjectStorageProtocol | None = None
    vicinity_client: VicinityClientProtocol | None = None
    session_factory: SessionFactory | None = None
