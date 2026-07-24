from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StoredObject:
    object_key: str
    last_modified: datetime


class ObjectStorageError(RuntimeError):
    """Raised when an object storage operation cannot be completed."""


class ObjectStorageProtocol(Protocol):
    def create_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        size_bytes: int,
    ) -> str: ...

    def object_exists(self, object_key: str) -> bool: ...

    def iter_objects(self, *, prefix: str) -> Iterable[StoredObject]: ...

    def delete_objects(self, object_keys: list[str]) -> None: ...
