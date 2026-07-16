from pydantic import ConfigDict, Field

from domain.estate.enums.estate_media_enums import MediaType
from schemas.parent_types import ResponseValidation
from schemas.types import ID


class EstateMediaResponse(ResponseValidation):
    id: ID
    object_key: str
    media_type: MediaType
    alt: str | None
    position: int = Field(ge=0)
    url: str

    model_config = ConfigDict(from_attributes=True)
