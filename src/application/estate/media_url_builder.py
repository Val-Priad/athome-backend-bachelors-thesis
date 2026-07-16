class MediaUrlBuilder:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def build(self, object_key: str) -> str:
        return f"{self._base_url}/{object_key.lstrip('/')}"
