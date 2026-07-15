from collections.abc import Collection
from typing import Protocol


class ObjectStorageProtocol(Protocol):
    def delete_objects(self, object_keys: Collection[str]) -> None: ...
