import pytest
from sqlalchemy import select

from domain.user.services.password_hasher import PasswordHasher
from domain.user.user_model import User
from exceptions.custom_exceptions.user_exceptions import (
    PasswordVerificationError,
)
from tests.integration.conftest import ME_PATH


def test_update_user_password_valid(client, db_session, logged_in_user):
    new_password = "new-password"
    response = client.patch(
        f"{ME_PATH}/password",
        json={
            "old_password": logged_in_user.password,
            "new_password": new_password,
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    db_session.expire_all()
    user = db_session.scalar(
        select(User).where(User.email == logged_in_user.email)
    )

    with pytest.raises(PasswordVerificationError):
        PasswordHasher.verify_password(
            logged_in_user.password, user.password_hash
        )

    PasswordHasher.verify_password(new_password, user.password_hash)


def test_update_user_password_old_password_matches_new(client, logged_in_user):
    response = client.patch(
        f"{ME_PATH}/password",
        json={
            "old_password": logged_in_user.password,
            "new_password": logged_in_user.password,
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 409


def test_update_user_password_old_password_is_wrong(client, logged_in_user):
    response = client.patch(
        f"{ME_PATH}/password",
        json={
            "old_password": "invalid-old-password",
            "new_password": logged_in_user.password,
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 401
