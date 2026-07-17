from typing import Protocol


class ObjectStorageError(RuntimeError):
    """Raised when an object storage operation cannot be completed."""


class ObjectStorageProtocol(Protocol):
    def create_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
    ) -> str: ...

    def object_exists(self, object_key: str) -> bool: ...

    def delete_object(self, object_key: str) -> None: ...

    def delete_objects(self, object_keys: list[str]) -> None: ...
