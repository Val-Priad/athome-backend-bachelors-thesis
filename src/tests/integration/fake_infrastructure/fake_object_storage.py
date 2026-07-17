from collections.abc import Collection


class FakeObjectStorage:
    def delete_objects(self, object_keys: Collection[str]) -> None:
        pass
