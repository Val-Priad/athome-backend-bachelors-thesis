from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from domain.password_reset.password_reset_model import PasswordReset
from domain.user.user_model import User
from tests.integration.conftest import AUTH_PATH


@pytest.fixture
def any_user(db_session):
    user = User(email="user@example.com", password_hash=b"hash")

    db_session.add(user)
    db_session.flush()

    password_reset = PasswordReset(
        user_id=user.id,
        token_hash=b"11111",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=5),
    )
    db_session.add(password_reset)
    db_session.flush()
    return {"user_id": user.id, "user_email": user.email}


def test_reset_password_token_valid(client, any_user, db_session, fake_mailer):
    response = client.post(
        f"{AUTH_PATH}/reset-password",
        json={"email": any_user["user_email"]},
    )

    assert response.status_code == 202

    qty_of_active_tokens = len(
        db_session.scalars(
            select(PasswordReset).where(
                PasswordReset.expires_at >= datetime.now(timezone.utc),
                PasswordReset.user_id == any_user["user_id"],
            )
        ).all()
    )
    assert qty_of_active_tokens == 1

    qty_of_tokens = len(
        db_session.scalars(
            select(PasswordReset).where(
                PasswordReset.user_id == any_user["user_id"],
            )
        ).all()
    )
    assert qty_of_tokens == 2
    assert len(fake_mailer.reset_emails) == 1
    assert fake_mailer.reset_emails[0][0] == any_user["user_email"]


def test_reset_password_token_no_user(client):
    response = client.post(
        f"{AUTH_PATH}/reset-password",
        json={"email": "user@example.com"},
    )

    assert response.status_code == 202


def test_reset_password_token_invalid_email(client):
    response = client.post(
        f"{AUTH_PATH}/reset-password",
        json={"email": "invalid_email"},
    )

    assert response.status_code == 400
