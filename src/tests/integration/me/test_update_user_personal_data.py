from uuid import uuid4

import pytest
from sqlalchemy import select

from application.ports.object_storage import ObjectStorageError
from domain.user.user_model import User
from tests.integration.conftest import ME_PATH


def _avatar_key(user_id, *, extension: str = "webp") -> str:
    return f"user-avatars/{user_id}/{uuid4()}.{extension}"


def _get_user(db_session, email: str) -> User:
    db_session.expire_all()
    return db_session.scalar(select(User).where(User.email == email))


def test_update_profile_requires_authentication(client):
    response = client.patch(
        f"{ME_PATH}/profile",
        json={"name": "Updated name"},
    )

    assert response.status_code == 401


def test_full_profile_update(
    client,
    db_session,
    logged_in_user,
    fake_object_storage,
):
    avatar_key = _avatar_key(logged_in_user.id)
    fake_object_storage.existing_object_keys = {avatar_key}
    updates = {
        "name": "Updated name",
        "phone_number": "+420701111111",
        "description": "Updated description",
        "avatar_key": avatar_key,
    }

    response = client.patch(
        f"{ME_PATH}/profile",
        json=updates,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert all(data[field] == value for field, value in updates.items())
    assert data["avatar_url"] == f"https://media.test/{avatar_key}"
    user = _get_user(db_session, logged_in_user.email)
    assert all(
        getattr(user, field) == value for field, value in updates.items()
    )


def test_avatar_can_be_cleared(
    client,
    db_session,
    logged_in_user,
):
    response = client.patch(
        f"{ME_PATH}/profile",
        json={"avatar_key": None},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["avatar_key"] is None
    assert data["avatar_url"] is None
    assert _get_user(db_session, logged_in_user.email).avatar_key is None


def test_existing_avatar_is_preserved_when_field_is_omitted(
    client,
    db_session,
    logged_in_user,
    fake_object_storage,
):
    original_avatar_key = _get_user(
        db_session, logged_in_user.email
    ).avatar_key
    fake_object_storage.object_exists_error = ObjectStorageError(
        "storage unavailable"
    )

    response = client.patch(
        f"{ME_PATH}/profile",
        json={"name": "Updated name"},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["name"] == "Updated name"
    assert data["avatar_key"] == original_avatar_key
    assert (
        _get_user(db_session, logged_in_user.email).avatar_key
        == original_avatar_key
    )


def test_individual_profile_field_is_updated(
    client,
    db_session,
    logged_in_user,
):
    original_user = _get_user(db_session, logged_in_user.email)
    original_name = original_user.name
    original_phone_number = original_user.phone_number

    response = client.patch(
        f"{ME_PATH}/profile",
        json={"description": "Only the description changed"},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["description"] == "Only the description changed"
    assert data["name"] == original_name
    assert data["phone_number"] == original_phone_number

    user = _get_user(db_session, logged_in_user.email)
    assert user.description == "Only the description changed"
    assert user.name == original_name
    assert user.phone_number == original_phone_number


def test_missing_avatar_object_returns_controlled_error(
    client,
    db_session,
    logged_in_user,
    fake_object_storage,
):
    avatar_key = _avatar_key(logged_in_user.id)
    original_name = _get_user(db_session, logged_in_user.email).name
    fake_object_storage.existing_object_keys = set()

    response = client.patch(
        f"{ME_PATH}/profile",
        json={"name": "Must not change", "avatar_key": avatar_key},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "media_object_not_found"
    assert _get_user(db_session, logged_in_user.email).name == original_name


@pytest.mark.parametrize(
    "avatar_key_factory",
    [
        pytest.param(
            lambda user_id: "invalid/avatar-key.webp",
            id="malformed",
        ),
        pytest.param(
            lambda user_id: _avatar_key(uuid4()),
            id="other_user",
        ),
        pytest.param(
            lambda user_id: f"estate-media/{user_id}/{uuid4()}.webp",
            id="estate_media",
        ),
    ],
)
def test_invalid_or_unowned_avatar_key_is_rejected(
    client,
    logged_in_user,
    avatar_key_factory,
):
    response = client.patch(
        f"{ME_PATH}/profile",
        json={"avatar_key": avatar_key_factory(logged_in_user.id)},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_media_object_key"


def test_storage_failure_returns_service_unavailable(
    client,
    db_session,
    logged_in_user,
    fake_object_storage,
):
    avatar_key = _avatar_key(logged_in_user.id)
    original_name = _get_user(db_session, logged_in_user.email).name
    fake_object_storage.object_exists_error = ObjectStorageError(
        "storage unavailable"
    )

    response = client.patch(
        f"{ME_PATH}/profile",
        json={"name": "Must not change", "avatar_key": avatar_key},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "media_upload_failed"
    assert _get_user(db_session, logged_in_user.email).name == original_name


def test_update_profile_validation(client, logged_in_user):
    response = client.patch(
        f"{ME_PATH}/profile",
        json={},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
