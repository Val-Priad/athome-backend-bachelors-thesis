import logging
from datetime import datetime, timedelta, timezone
from typing import cast

from sqlalchemy import CursorResult, delete

from application.transactions import TransactionManagerProtocol
from domain.user.user_model import User

_logger = logging.getLogger(__name__)


def cleanup_unverified_users(
    transactions: TransactionManagerProtocol,
) -> None:
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        with transactions.session() as session:
            result = cast(
                CursorResult,
                session.execute(
                    delete(User).where(
                        User.is_email_verified.is_(False),
                        User.created_at < cutoff,
                    )
                ),
            )
        _logger.info(
            "Successfully deleted %s unverified users", result.rowcount
        )
    except Exception:
        _logger.exception("Error occurred during deletion of unverified users")
