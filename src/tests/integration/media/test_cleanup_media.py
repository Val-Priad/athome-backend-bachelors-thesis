from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from application.ports.object_storage import ObjectStorageError, StoredObject
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.models.estate_media_model import EstateMedia
from domain.media.media_enums import MediaType
from domain.user.user_model import User, UserRole
from tests.integration.conftest import MEDIA_PATH
from tests.integration.estate.test_filter_estate import create_filter_estate


def _object_key(uploader_id) -> str:
    return f"estate-media/{uploader_id}/{uuid4()}.webp"


def _avatar_key(uploader_id) -> str:
    return f"user-avatars/{uploader_id}/{uuid4()}.webp"


def test_cleanup_requires_authentication(client):
    response = client.post(
        f"{MEDIA_PATH}/cleanup",
        json={
            "purpose": "estate",
            "object_keys": [
                f"estate-media/{uuid4()}/{uuid4()}.webp",
            ],
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
@pytest.mark.parametrize(
    ("purpose", "object_key_factory"),
    [
        ("estate", _object_key),
        ("user_avatar", _avatar_key),
    ],
)
def test_cleanup_deletes_owned_unused_objects_for_each_purpose(
    client,
    logged_in_user,
    fake_object_storage,
    purpose,
    object_key_factory,
):
    object_keys = [
        object_key_factory(logged_in_user.id),
        object_key_factory(logged_in_user.id),
    ]

    response = client.post(
        f"{MEDIA_PATH}/cleanup",
        json={"purpose": purpose, "object_keys": object_keys},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200
    assert fake_object_storage.deleted_object_keys == object_keys


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_cleanup_rejects_another_uploaders_object(
    client,
    logged_in_user,
    fake_object_storage,
):
    response = client.post(
        f"{MEDIA_PATH}/cleanup",
        json={
            "purpose": "estate",
            "object_keys": [_object_key(uuid4())],
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_media_object_key"
    assert fake_object_storage.deleted_object_keys == []


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_cleanup_rejects_duplicate_object_keys(
    client,
    logged_in_user,
    fake_object_storage,
):
    object_key = _object_key(logged_in_user.id)

    response = client.post(
        f"{MEDIA_PATH}/cleanup",
        json={
            "purpose": "estate",
            "object_keys": [object_key, object_key],
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "request_validation_error"
    assert fake_object_storage.deleted_object_keys == []


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_cleanup_rejects_key_from_another_purpose(
    client,
    logged_in_user,
    fake_object_storage,
):
    object_key = f"estate-media/{logged_in_user.id}/{uuid4()}.webp"

    response = client.post(
        f"{MEDIA_PATH}/cleanup",
        json={
            "purpose": "user_avatar",
            "object_keys": [object_key],
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_media_object_key"
    assert fake_object_storage.deleted_object_keys == []


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_cleanup_rejects_object_used_by_estate(
    client,
    db_session,
    logged_in_user,
    fake_object_storage,
):
    object_key = _object_key(logged_in_user.id)
    create_filter_estate(
        db_session,
        title="Cleanup protected estate",
        status=ListingStatus.draft,
        media=[
            EstateMedia(
                object_key=object_key,
                media_type=MediaType.image,
                position=0,
            )
        ],
    )

    response = client.post(
        f"{MEDIA_PATH}/cleanup",
        json={"purpose": "estate", "object_keys": [object_key]},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "media_object_already_used"
    assert fake_object_storage.deleted_object_keys == []


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_cleanup_maps_object_storage_error(
    client,
    logged_in_user,
    fake_object_storage,
):
    object_key = _object_key(logged_in_user.id)
    fake_object_storage.delete_error = ObjectStorageError("S3 unavailable")

    response = client.post(
        f"{MEDIA_PATH}/cleanup",
        json={
            "purpose": "estate",
            "object_keys": [object_key],
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "media_upload_failed"
    assert fake_object_storage.deleted_object_keys == []


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_cleanup_rejects_avatar_used_by_user(
    client,
    db_session,
    logged_in_user,
    fake_object_storage,
):
    object_key = _avatar_key(logged_in_user.id)
    user = db_session.get(User, logged_in_user.id)
    assert user is not None
    user.avatar_key = object_key
    db_session.flush()

    response = client.post(
        f"{MEDIA_PATH}/cleanup",
        json={
            "purpose": "user_avatar",
            "object_keys": [object_key],
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "media_object_already_used"
    assert fake_object_storage.deleted_object_keys == []


def test_orphan_cleanup_preserves_real_database_references(
    application_container,
    db_session,
    any_user,
    fake_object_storage,
):
    used_estate_key = _object_key(any_user.id)
    orphan_estate_key = _object_key(any_user.id)
    used_avatar_key = _avatar_key(any_user.id)
    orphan_avatar_key = _avatar_key(any_user.id)

    create_filter_estate(
        db_session,
        title="Orphan cleanup protected estate",
        status=ListingStatus.draft,
        media=[
            EstateMedia(
                object_key=used_estate_key,
                media_type=MediaType.image,
                position=0,
            )
        ],
    )
    any_user.avatar_key = used_avatar_key
    db_session.flush()

    old = datetime.now(timezone.utc) - timedelta(days=2)
    fake_object_storage.stored_objects = [
        StoredObject(used_estate_key, old),
        StoredObject(orphan_estate_key, old),
        StoredObject(used_avatar_key, old),
        StoredObject(orphan_avatar_key, old),
    ]

    result = application_container.media.cleanup_orphans.execute()

    assert fake_object_storage.deleted_object_keys == [
        orphan_estate_key,
        orphan_avatar_key,
    ]
    assert result.used == 2
    assert result.deleted == 2
