import pytest

from domain.user.user_model import User
from tests.integration.conftest import AUTH_PATH, TEST_PASSWORD


@pytest.fixture
def verified_user(db_session, test_password_hash):
    user = User(
        email="user@example.com",
        password_hash=test_password_hash,
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.flush()

    return {"email": user.email, "password": TEST_PASSWORD}


@pytest.fixture
def unverified_user(db_session, test_password_hash):
    user = User(
        email="user@example.com",
        password_hash=test_password_hash,
        is_email_verified=False,
    )
    db_session.add(user)
    db_session.flush()

    return {"email": user.email, "password": TEST_PASSWORD}


def test_login_and_log_out(client, verified_user):
    login_response = client.post(
        f"{AUTH_PATH}/login",
        json={
            "email": verified_user["email"],
            "password": verified_user["password"],
        },
    )
    assert login_response.status_code == 200

    logout_response = client.post(
        f"{AUTH_PATH}/logout",
        headers={"X-CSRF-TOKEN": client.get_cookie("csrf_access_token").value},
    )
    assert logout_response.status_code == 200


def test_login_unverified_user(client, unverified_user):
    login_response = client.post(
        f"{AUTH_PATH}/login",
        json={
            "email": unverified_user["email"],
            "password": unverified_user["password"],
        },
    )
    assert login_response.status_code == 401


def test_login_not_registered_user(client):
    login_response = client.post(
        f"{AUTH_PATH}/login",
        json={
            "email": "not_registered@example.com",
            "password": "not_registered",  # NOSONAR
        },
    )
    assert login_response.status_code == 401


def test_login_invalid_password(client, verified_user):
    login_response = client.post(
        f"{AUTH_PATH}/login",
        json={
            "email": verified_user["email"],
            "password": "wrong_password",
        },
    )
    assert login_response.status_code == 401
