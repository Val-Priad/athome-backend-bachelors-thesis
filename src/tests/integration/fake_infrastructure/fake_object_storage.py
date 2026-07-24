from collections.abc import Iterator

from application.ports.object_storage import ObjectStorageError, StoredObject


class FakeObjectStorage:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.existing_object_keys: set[str] | None = None
        self.checked_object_keys: list[str] = []
        self.object_exists_error: ObjectStorageError | None = None
        self.deleted_object_keys: list[str] = []
        self.delete_error: Exception | None = None
        self.stored_objects: list[StoredObject] = []

    def create_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        size_bytes: int,
    ) -> str:
        return f"https://storage.test/{object_key}"

    def object_exists(self, object_key: str) -> bool:
        self.checked_object_keys.append(object_key)
        if self.object_exists_error is not None:
            raise self.object_exists_error
        return (
            True
            if self.existing_object_keys is None
            else object_key in self.existing_object_keys
        )

    def iter_objects(self, *, prefix: str) -> Iterator[StoredObject]:
        yield from (
            stored_object
            for stored_object in self.stored_objects
            if stored_object.object_key.startswith(prefix)
        )

    def delete_objects(self, object_keys: list[str]) -> None:
        if self.delete_error is not None:
            raise self.delete_error

        self.deleted_object_keys.extend(object_keys)
