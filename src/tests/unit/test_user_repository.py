from unittest.mock import Mock

from domain.user.user_repository import UserRepository


def test_get_used_avatar_keys_returns_matching_non_null_keys() -> None:
    session = Mock()
    session.scalars.return_value = iter(["user-avatars/used.webp", None])

    result = UserRepository().get_used_avatar_keys(
        session,
        ["user-avatars/used.webp", "user-avatars/unused.webp"],
    )

    assert result == {"user-avatars/used.webp"}
    session.scalars.assert_called_once()


def test_get_used_avatar_keys_returns_empty_set_without_query() -> None:
    session = Mock()

    result = UserRepository().get_used_avatar_keys(session, [])

    assert result == set()
    session.scalars.assert_not_called()
