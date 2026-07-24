from collections.abc import Iterator

from application.ports.object_storage import StoredObject


class NoOpObjectStorage:
    def create_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        size_bytes: int,
    ) -> str:
        return ""

    def object_exists(self, object_key: str) -> bool:
        return False

    def iter_objects(self, *, prefix: str) -> Iterator[StoredObject]:
        yield from ()

    def delete_object(self, object_key: str) -> None:
        pass

    def delete_objects(self, object_keys: list[str]) -> None:
        pass
