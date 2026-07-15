from collections.abc import Collection


class NoOpObjectStorage:
    def delete_objects(self, object_keys: Collection[str]) -> None:
        pass
