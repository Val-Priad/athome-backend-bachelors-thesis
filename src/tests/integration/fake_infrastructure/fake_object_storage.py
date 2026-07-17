class FakeObjectStorage:
    def create_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
    ) -> str:
        return f"https://storage.test/{object_key}"

    def object_exists(self, object_key: str) -> bool:
        return True

    def delete_object(self, object_key: str) -> None:
        pass

    def delete_objects(self, object_keys: list[str]) -> None:
        pass
