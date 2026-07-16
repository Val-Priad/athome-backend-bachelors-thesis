from flask import current_app
from pydantic import ConfigDict, Field, computed_field

from domain.estate.enums.estate_media_enums import MediaType
from schemas.parent_types import ResponseValidation
from schemas.types import ID


class EstateMediaResponse(ResponseValidation):
    id: ID
    object_key: str
    media_type: MediaType
    alt: str | None
    position: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def url(self) -> str:
        base_url = current_app.config["MEDIA_BASE_URL"]
        return f"{base_url.rstrip('/')}/{self.object_key.lstrip('/')}"
