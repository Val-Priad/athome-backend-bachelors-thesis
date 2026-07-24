from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from domain.user.user_model import User


def test_cleanup_unverified_users_removes_only_expired_unverified_users(
    app,
    db_session,
    test_password_hash,
) -> None:
    now = datetime.now(timezone.utc)
    expired_unverified = User(
        email="expired-unverified@example.com",
        password_hash=test_password_hash,
        is_email_verified=False,
        created_at=now - timedelta(hours=25),
    )
    fresh_unverified = User(
        email="fresh-unverified@example.com",
        password_hash=test_password_hash,
        is_email_verified=False,
        created_at=now - timedelta(hours=23),
    )
    expired_verified = User(
        email="expired-verified@example.com",
        password_hash=test_password_hash,
        is_email_verified=True,
        created_at=now - timedelta(hours=25),
    )
    db_session.add_all(
        [expired_unverified, fresh_unverified, expired_verified]
    )
    db_session.commit()

    result = app.test_cli_runner().invoke(args=["users", "cleanup-unverified"])

    assert result.exit_code == 0
    assert "deleted=1" in result.output
    remaining_emails = set(db_session.scalars(select(User.email)))
    assert expired_unverified.email not in remaining_emails
    assert fresh_unverified.email in remaining_emails
    assert expired_verified.email in remaining_emails
