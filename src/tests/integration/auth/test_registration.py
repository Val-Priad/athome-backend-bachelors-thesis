import pytest
from sqlalchemy import select

from domain.email_verification.email_verification_model import (
    EmailVerification,
)
from domain.user.services.password_hasher import PasswordHasher
from domain.user.user_model import User
from tests.integration.conftest import AUTH_PATH


def test_register_valid(client, db_session, fake_mailer):
    password = "some_password"
    response = client.post(
        f"{AUTH_PATH}/register",
        json={"email": "user@example.com", "password": password},
    )

    assert response.status_code == 202

    user = db_session.scalar(
        select(User).where(User.email == "user@example.com")
    )
    assert user is not None
    assert PasswordHasher.verify_password(password, user.password_hash) is None

    email_verification = db_session.scalar(
        select(EmailVerification).where(EmailVerification.user_id == user.id)
    )
    assert email_verification is not None
    assert len(fake_mailer.verification_emails) == 1
    assert fake_mailer.verification_emails[0][0] == user.email


def test_register_user_already_exists(client):
    payload = {
        "email": "user@example.com",
        "password": "some_password",
    }
    client.post(f"{AUTH_PATH}/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 202


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {"email": "imposter", "password": "valid_password"},
            id="invalid email format",
        ),
        pytest.param(
            {"email": "user@example.com", "password": "       "},  # NOSONAR
            id="invalid password (after strip)",
        ),
        pytest.param({"email": "user@example.com"}, id="missing password"),
        pytest.param({"password": "valid_password"}, id="missing email"),
        pytest.param({"email": 6, "password": 7}, id="invalid types"),
    ],
)
def test_register_user_validation_error(client, payload):
    response = client.post(
        f"{AUTH_PATH}/register",
        json=payload,
    )
    assert response.status_code == 400


def test_register_internal_error_rolls_back(
    client,
    db_session,
    application_container,
    monkeypatch,
):
    def boom(db, email, password):  # Do not touch arguments!
        user = User(email=email, password_hash=b"hash")  # NOSONAR
        db.add(user)
        db.flush()
        raise Exception("boom")  # NOSONAR

    monkeypatch.setattr(
        application_container.auth.register_user._auth_service,
        "create_user",
        boom,
    )

    response = client.post(
        f"{AUTH_PATH}/register",
        json={"email": "user@example.com", "password": "some_password"},
    )
    assert response.status_code == 500

    saved_user = db_session.scalar(
        select(User).where(User.email == "user@example.com")
    )
    assert saved_user is None
