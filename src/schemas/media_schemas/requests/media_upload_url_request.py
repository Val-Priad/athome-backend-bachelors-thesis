from enum import Enum
from typing import Annotated

from pydantic import Field, ValidationInfo, field_validator
from pydantic.functional_validators import BeforeValidator

from domain.media.media_enums import MediaPurpose
from schemas.parent_types import RequestValidation
from schemas.validators.user_validators import strip_string

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_SIZE_BYTES = 100 * 1024 * 1024


class MediaContentType(str, Enum):
    jpeg = "image/jpeg"
    png = "image/png"
    webp = "image/webp"
    mp4 = "video/mp4"

    @property
    def extension(self) -> str:
        if self is MediaContentType.jpeg:
            return "jpg"

        return self.value.rsplit("/", maxsplit=1)[1]

    @property
    def is_image(self) -> bool:
        return self.value.startswith("image/")

    @property
    def max_size_bytes(self) -> int:
        if self.is_image:
            return MAX_IMAGE_SIZE_BYTES

        return MAX_VIDEO_SIZE_BYTES


class MediaUploadUrlRequest(RequestValidation):
    purpose: MediaPurpose
    filename: Annotated[
        str,
        BeforeValidator(strip_string),
        Field(min_length=1, max_length=255),
    ]
    content_type: MediaContentType
    size_bytes: int = Field(gt=0)

    @field_validator("content_type")
    @classmethod
    def _validate_content_type_for_purpose(
        cls,
        content_type: MediaContentType,
        info: ValidationInfo,
    ) -> MediaContentType:
        if (
            info.data.get("purpose") is MediaPurpose.user_avatar
            and not content_type.is_image
        ):
            raise ValueError("User avatar must be an image")

        return content_type

    @field_validator("size_bytes")
    @classmethod
    def _validate_max_size(
        cls,
        size_bytes: int,
        info: ValidationInfo,
    ) -> int:
        content_type = info.data.get("content_type")
        if not isinstance(content_type, MediaContentType):
            return size_bytes

        if size_bytes > content_type.max_size_bytes:
            media_kind = "Image" if content_type.is_image else "Video"
            raise ValueError(
                f"{media_kind} size must not exceed "
                f"{content_type.max_size_bytes} bytes"
            )

        return size_bytes
