from pydantic import Field

from domain.estate.enums.estate_media_enums import MediaType
from schemas.parent_types import RequestValidation


class EstateMediaSection(RequestValidation):
    object_key: str = Field(min_length=1, max_length=1024)
    media_type: MediaType
    alt: str | None = Field(default=None, max_length=255)
