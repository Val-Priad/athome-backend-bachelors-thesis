from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from domain.email_verification.email_verification_model import (
    EmailVerification,
)
from domain.user.user_model import User
from tests.integration.conftest import AUTH_PATH


@pytest.fixture
def unverified_user(db_session):
    user = User(email="user@example.com", password_hash=b"hash")  # NOSONAR
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def verified_user(db_session):
    user = User(
        email="user@example.com",
        password_hash=b"hash",  # NOSONAR
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def previous_token(db_session, unverified_user):
    email_verification = EmailVerification(
        user_id=unverified_user.id,
        token_hash=b"hash",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db_session.add(email_verification)
    db_session.flush()
    return email_verification


def test_resend_verification_valid(
    client, unverified_user, db_session, previous_token, fake_mailer
):
    previous_token_id = previous_token.id
    unverified_user_id = unverified_user.id

    response = client.post(
        f"{AUTH_PATH}/resend-verification-email",
        json={"email": unverified_user.email},
    )

    assert response.status_code == 202

    qty_of_active_tokens = len(
        db_session.scalars(
            select(EmailVerification).where(
                EmailVerification.expires_at > datetime.now(timezone.utc),
                EmailVerification.user_id == unverified_user_id,
            )
        ).all()
    )
    assert qty_of_active_tokens == 1

    qty_of_tokens = len(
        db_session.scalars(
            select(EmailVerification).where(
                EmailVerification.user_id == unverified_user_id,
            )
        ).all()
    )
    assert qty_of_tokens == 2

    deactivated_token = db_session.scalar(
        select(EmailVerification).where(
            EmailVerification.expires_at < datetime.now(timezone.utc),
            EmailVerification.user_id == unverified_user_id,
        )
    )

    assert previous_token_id == deactivated_token.id
    assert len(fake_mailer.verification_emails) == 1
    assert fake_mailer.verification_emails[0][0] == unverified_user.email


def test_resend_verification_validation(client):
    response = client.post(
        f"{AUTH_PATH}/resend-verification-email",
        json={"email": "invalid_email"},
    )

    assert response.status_code == 400


def test_resend_verification_if_user_not_found(client):
    response = client.post(
        f"{AUTH_PATH}/resend-verification-email",
        json={"email": "user_does_not_exist@example.com"},
    )

    assert response.status_code == 202


def test_resend_verification_if_user_already_verified(client, verified_user):
    response = client.post(
        f"{AUTH_PATH}/resend-verification-email",
        json={"email": verified_user.email},
    )

    assert response.status_code == 202


def test_resend_verification_on_server_error_returns_500(
    client,
    unverified_user,
    application_container,
    monkeypatch,
):
    def boom(*args, **kwargs):  # Do not touch arguments!
        raise Exception("boom")  # NOSONAR

    monkeypatch.setattr(
        application_container.auth.resend_verification._email_verification_service,
        "create_token",
        boom,
    )

    response = client.post(
        f"{AUTH_PATH}/resend-verification-email",
        json={"email": unverified_user.email},
    )

    assert response.status_code == 500
