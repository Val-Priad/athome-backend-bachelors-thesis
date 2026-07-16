from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApplicationUrls:
    app_base_url: str
    media_base_url: str
