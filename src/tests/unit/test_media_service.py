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


@pytest.mark.parametrize(
    ("object_key", "purpose"),
    [
        pytest.param(
            IMAGE_KEY,
            MediaPurpose.estate,
            id="estate",
        ),
        pytest.param(
            f"user-avatars/{UPLOADER_ID}/{MEDIA_ID}.jpg",
            MediaPurpose.user_avatar,
            id="user_avatar",
        ),
    ],
)
def test_accepts_valid_generated_object_key_for_each_purpose(
    object_key: str,
    purpose: MediaPurpose,
) -> None:
    service, object_storage = _service()

    service.validate_object(
        object_key=object_key,
        uploader_id=UPLOADER_ID,
        purpose=purpose,
        media_type=MediaType.image,
    )

    object_storage.object_exists.assert_called_once_with(object_key)


def test_validates_owned_key_without_accessing_storage() -> None:
    service, object_storage = _service()

    service.validate_owned_object_key(
        object_key=IMAGE_KEY,
        uploader_id=UPLOADER_ID,
        purpose=MediaPurpose.estate,
        media_type=MediaType.image,
    )

    object_storage.object_exists.assert_not_called()


def test_validate_objects_checks_all_items_until_one_is_missing() -> None:
    service, object_storage = _service()
    second_media_id = UUID("40000000-0000-0000-0000-000000000def")
    second_key = f"estate-media/{UPLOADER_ID}/{second_media_id}.mp4"
    object_storage.object_exists.side_effect = lambda object_key: (
        object_key != second_key
    )
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

    with pytest.raises(MediaObjectNotFoundError):
        service.validate_objects(
            media=media,
            uploader_id=UPLOADER_ID,
            purpose=MediaPurpose.estate,
        )

    assert object_storage.object_exists.call_args_list == [
        call(IMAGE_KEY),
        call(second_key),
    ]


@pytest.mark.parametrize(
    ("object_key", "purpose"),
    [
        (
            f"unexpected-prefix/{UPLOADER_ID}/{MEDIA_ID}.webp",
            MediaPurpose.estate,
        ),
        (
            f"estate-media/{OTHER_UPLOADER_ID}/{MEDIA_ID}.webp",
            MediaPurpose.estate,
        ),
        (
            f"estate-media/{UPLOADER_ID}/nested/{MEDIA_ID}.webp",
            MediaPurpose.estate,
        ),
        (IMAGE_KEY, MediaPurpose.user_avatar),
    ],
)
def test_rejects_keys_outside_security_boundary(
    object_key: str,
    purpose: MediaPurpose,
) -> None:
    service, object_storage = _service()

    with pytest.raises(InvalidMediaObjectKeyError):
        service.validate_object(
            object_key=object_key,
            uploader_id=UPLOADER_ID,
            purpose=purpose,
            media_type=MediaType.image,
        )

    object_storage.object_exists.assert_not_called()


@pytest.mark.parametrize(
    "object_key",
    [
        f"estate-media/{UPLOADER_ID}/image.webp",
        f"estate-media/{UPLOADER_ID}/{str(MEDIA_ID).upper()}.webp",
        f"estate-media/{UPLOADER_ID}/{MEDIA_ID}.webp.backup",
        f"estate-media/{UPLOADER_ID}/{MEDIA_ID}.WEBP",
        f"estate-media/{UPLOADER_ID}/{MEDIA_ID}.gif",
    ],
)
def test_rejects_noncanonical_or_unsupported_filename(
    object_key: str,
) -> None:
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
