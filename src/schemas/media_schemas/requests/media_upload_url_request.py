from typing import Annotated, Literal

from pydantic import Field, ValidationInfo, field_validator
from pydantic.functional_validators import BeforeValidator

from schemas.parent_types import RequestValidation
from schemas.validators.user_validators import strip_string

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_SIZE_BYTES = 100 * 1024 * 1024

IMAGE_CONTENT_TYPES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
    }
)


class MediaUploadUrlRequest(RequestValidation):
    filename: Annotated[
        str,
        BeforeValidator(strip_string),
        Field(min_length=1, max_length=255),
    ]
    content_type: Literal[
        "image/jpeg",
        "image/png",
        "image/webp",
        "video/mp4",
    ]
    size_bytes: int = Field(gt=0)

    @field_validator("size_bytes")
    @classmethod
    def _validate_max_size(
        cls,
        size_bytes: int,
        info: ValidationInfo,
    ) -> int:
        content_type = info.data.get("content_type")
        if content_type in IMAGE_CONTENT_TYPES:
            max_size = MAX_IMAGE_SIZE_BYTES
            media_kind = "Image"
        elif content_type == "video/mp4":
            max_size = MAX_VIDEO_SIZE_BYTES
            media_kind = "Video"
        else:
            return size_bytes

        if size_bytes > max_size:
            raise ValueError(
                f"{media_kind} size must not exceed {max_size} bytes"
            )

        return size_bytes
