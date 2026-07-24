from pydantic import ConfigDict, Field, field_validator

from domain.media.media_enums import MediaPurpose
from schemas.parent_types import RequestValidation


class MediaCleanupRequest(RequestValidation):
    model_config = ConfigDict(extra="forbid")

    purpose: MediaPurpose
    object_keys: list[str] = Field(min_length=1, max_length=100)

    @field_validator("object_keys")
    @classmethod
    def validate_object_keys(cls, object_keys: list[str]) -> list[str]:
        if len(object_keys) != len(set(object_keys)):
            raise ValueError("Media object_key values must be unique")

        return object_keys
