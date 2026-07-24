from unittest.mock import Mock, call
from uuid import UUID

import pytest

from application.ports.object_storage import ObjectStorageError
from domain.media.media_enums import MediaPurpose, MediaType
from domain.media.media_service import MediaService
from exceptions.custom_exceptions.media_exceptions import (
    InvalidMediaObjectKeyError,
    MediaObjectNotFoundError,
    MediaUploadError,
)
from schemas.estate_schemas.sections.media_section import EstateMediaSection

UPLOADER_ID = UUID("10000000-0000-0000-0000-000000000001")
OTHER_UPLOADER_ID = UUID("20000000-0000-0000-0000-000000000002")
MEDIA_ID = UUID("30000000-0000-0000-0000-000000000abc")
IMAGE_KEY = f"estate-media/{UPLOADER_ID}/{MEDIA_ID}.webp"


def _service(
    *,
    object_exists: bool = True,
) -> tuple[MediaService, Mock]:
    object_storage = Mock()
    object_storage.object_exists.return_value = object_exists
    return MediaService(object_storage), object_storage


def test_validates_backend_generated_estate_media_key() -> None:
    service, object_storage = _service()

    service.validate_object(
        object_key=IMAGE_KEY,
        uploader_id=UPLOADER_ID,
        purpose=MediaPurpose.estate,
        media_type=MediaType.image,
    )

    object_storage.object_exists.assert_called_once_with(IMAGE_KEY)


def test_validates_owned_key_without_accessing_storage() -> None:
    service, object_storage = _service()

    service.validate_owned_object_key(
        object_key=IMAGE_KEY,
        uploader_id=UPLOADER_ID,
        purpose=MediaPurpose.estate,
        media_type=MediaType.image,
    )

    object_storage.object_exists.assert_not_called()


def test_validates_multiple_objects() -> None:
    service, object_storage = _service()
    second_media_id = UUID("40000000-0000-0000-0000-000000000def")
    second_key = f"estate-media/{UPLOADER_ID}/{second_media_id}.mp4"
    media = [
        EstateMediaSection(
            object_key=IMAGE_KEY,
            media_type=MediaType.image,
        ),
        EstateMediaSection(
            object_key=second_key,
            media_type=MediaType.video,
        ),
    ]

    service.validate_objects(
        media=media,
        uploader_id=UPLOADER_ID,
        purpose=MediaPurpose.estate,
    )

    assert object_storage.object_exists.call_args_list == [
        call(IMAGE_KEY),
        call(second_key),
    ]


def test_empty_media_does_not_access_storage() -> None:
    service, object_storage = _service()

    service.validate_objects(
        media=[],
        uploader_id=UPLOADER_ID,
        purpose=MediaPurpose.estate,
    )

    object_storage.object_exists.assert_not_called()


@pytest.mark.parametrize(
    "object_key",
    [
        f"user-avatars/{UPLOADER_ID}/{MEDIA_ID}.webp",
        f"estate-media/{OTHER_UPLOADER_ID}/{MEDIA_ID}.webp",
        f"estate-media/{UPLOADER_ID}/nested/{MEDIA_ID}.webp",
        f"estate-media/{UPLOADER_ID}/image.webp",
        f"estate-media/{UPLOADER_ID}/hello.world.webp",
        f"estate-media/{UPLOADER_ID}/{str(MEDIA_ID).upper()}.webp",
        f"estate-media/{UPLOADER_ID}/{MEDIA_ID}.WEBP",
    ],
)
def test_rejects_invalid_estate_media_key(object_key: str) -> None:
    service, object_storage = _service()

    with pytest.raises(InvalidMediaObjectKeyError):
        service.validate_object(
            object_key=object_key,
            uploader_id=UPLOADER_ID,
            purpose=MediaPurpose.estate,
            media_type=MediaType.image,
        )

    object_storage.object_exists.assert_not_called()


@pytest.mark.parametrize(
    ("object_key", "media_type"),
    [
        (f"estate-media/{UPLOADER_ID}/{MEDIA_ID}.mp4", MediaType.image),
        (IMAGE_KEY, MediaType.video),
    ],
)
def test_rejects_extension_not_allowed_for_media_type(
    object_key: str,
    media_type: MediaType,
) -> None:
    service, object_storage = _service()

    with pytest.raises(InvalidMediaObjectKeyError):
        service.validate_object(
            object_key=object_key,
            uploader_id=UPLOADER_ID,
            purpose=MediaPurpose.estate,
            media_type=media_type,
        )

    object_storage.object_exists.assert_not_called()


def test_rejects_missing_object() -> None:
    service, _ = _service(object_exists=False)

    with pytest.raises(MediaObjectNotFoundError):
        service.validate_object(
            object_key=IMAGE_KEY,
            uploader_id=UPLOADER_ID,
            purpose=MediaPurpose.estate,
            media_type=MediaType.image,
        )


def test_wraps_object_storage_error() -> None:
    object_storage = Mock()
    storage_error = ObjectStorageError("S3 unavailable")
    object_storage.object_exists.side_effect = storage_error
    service = MediaService(object_storage)

    with pytest.raises(MediaUploadError) as raised:
        service.validate_object(
            object_key=IMAGE_KEY,
            uploader_id=UPLOADER_ID,
            purpose=MediaPurpose.estate,
            media_type=MediaType.image,
        )

    assert raised.value.__cause__ is storage_error


def test_uses_requested_purpose() -> None:
    service, object_storage = _service()
    avatar_key = f"user-avatars/{UPLOADER_ID}/{MEDIA_ID}.jpg"

    service.validate_object(
        object_key=avatar_key,
        uploader_id=UPLOADER_ID,
        purpose=MediaPurpose.user_avatar,
        media_type=MediaType.image,
    )

    object_storage.object_exists.assert_called_once_with(avatar_key)


def test_rejects_key_from_another_purpose() -> None:
    service, object_storage = _service()

    with pytest.raises(InvalidMediaObjectKeyError):
        service.validate_object(
            object_key=IMAGE_KEY,
            uploader_id=UPLOADER_ID,
            purpose=MediaPurpose.user_avatar,
            media_type=MediaType.image,
        )

    object_storage.object_exists.assert_not_called()
