from uuid import uuid4

import pytest

from domain.user.user_model import UserRole
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UserResponse,
)
from tests.integration.conftest import ADMIN_USERS_PATH


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_get_user_by_id_valid(client, logged_in_user, any_user, db_session):
    any_user.avatar_key = f"user-avatars/{any_user.id}/{uuid4()}.webp"
    db_session.flush()
    response = client.get(
        f"{ADMIN_USERS_PATH}/{any_user.id}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    body = response.get_json()
    data = body["data"]

    user_dto = UserResponse.from_model(any_user)
    user_json = user_dto.model_dump(mode="json")
    user_json["avatar_url"] = f"https://media.test/{any_user.avatar_key}"

    assert data == user_json


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_get_user_by_id_user_not_found(client, logged_in_user):
    response = client.get(
        f"{ADMIN_USERS_PATH}/{uuid4()}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "user_not_found"


@pytest.mark.parametrize(
    "logged_in_user", [UserRole.agent, UserRole.user], indirect=True
)
def test_get_user_by_id_forbidden(client, logged_in_user, any_user):
    response = client.get(
        f"{ADMIN_USERS_PATH}/{any_user.id}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "forbidden"
