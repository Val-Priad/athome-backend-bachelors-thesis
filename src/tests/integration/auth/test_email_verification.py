import secrets
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from domain.email_verification.email_verification_model import (
    EmailVerification,
)
from domain.token.token_generator import TokenGenerator
from domain.user.user_model import User
from tests.integration.conftest import AUTH_PATH


@pytest.fixture
def raw_token_verification_id_user_id(db_session):
    user = User(email="user@example.com", password_hash=b"hash")
    db_session.add(user)
    db_session.flush()

    raw_token = secrets.token_urlsafe(32)
    hashed_token = TokenGenerator.hash_token(raw_token)
    email_verification = EmailVerification(
        user_id=user.id,
        token_hash=hashed_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db_session.add(email_verification)
    db_session.flush()

    return raw_token, email_verification.id, user.id


@pytest.fixture
def expired_raw_token_verification_id_user_id(db_session):
    user = User(email="user@example.com", password_hash=b"hash")
    db_session.add(user)
    db_session.flush()

    raw_token = secrets.token_urlsafe(32)
    hashed_token = TokenGenerator.hash_token(raw_token)
    email_verification = EmailVerification(
        user_id=user.id,
        token_hash=hashed_token,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=24),
    )
    db_session.add(email_verification)
    db_session.flush()

    return raw_token, email_verification.id, user.id


def test_token_verification_valid(
    client, raw_token_verification_id_user_id, db_session
):
    raw_token, email_verification_id, user_id = (
        raw_token_verification_id_user_id
    )

    now = datetime.now(timezone.utc)

    response = client.get(
        f"{AUTH_PATH}/verify-email",
        query_string={"token": raw_token},
    )

    assert response.status_code == 200

    email_verification = db_session.scalar(
        select(EmailVerification).where(
            EmailVerification.id == email_verification_id
        )
    )
    assert email_verification.used_at >= now

    user = db_session.scalar(select(User).where(User.id == user_id))
    assert user.is_email_verified


@pytest.mark.parametrize(
    "query_string",
    [
        pytest.param(
            {"token": ""},
            id="empty_token",
        ),
        pytest.param(
            {"token": "a" * 55},
            id="token_too_long",
        ),
        pytest.param(
            {"token": "67"},
            id="token_too_short",
        ),
        pytest.param(
            {},
            id="missing_token",
        ),
    ],
)
def test_token_verification_token_validation(client, query_string):
    response = client.get(
        f"{AUTH_PATH}/verify-email",
        query_string=query_string,
    )

    assert response.status_code == 400


def test_token_verification_token_expired(
    client, expired_raw_token_verification_id_user_id
):
    raw_token, _, _ = expired_raw_token_verification_id_user_id

    response = client.get(
        f"{AUTH_PATH}/verify-email",
        query_string={"token": raw_token},
    )

    assert response.status_code == 401

    body = response.get_json()
    assert body["error"] == {
        "code": "token_invalid",
        "message": "Token invalid",
    }
