from unittest.mock import Mock

from domain.estate.estate_media_repository import EstateMediaRepository
from domain.media.media_enums import MediaPurpose
from domain.media.media_usage_service import MediaUsageService
from domain.user.user_repository import UserRepository


def _service() -> tuple[MediaUsageService, Mock, Mock]:
    estate_repository = Mock(spec=EstateMediaRepository)
    user_repository = Mock(spec=UserRepository)
    return (
        MediaUsageService(
            estate_media_repository=estate_repository,
            user_repository=user_repository,
        ),
        estate_repository,
        user_repository,
    )


def test_get_used_object_keys_uses_estate_repository() -> None:
    service, estate_repository, user_repository = _service()
    session = Mock()
    keys = ["estate-media/used.webp", "estate-media/unused.webp"]
    estate_repository.get_used_object_keys.return_value = {keys[0]}

    result = service.get_used_object_keys(
        session=session,
        purpose=MediaPurpose.estate,
        object_keys=keys,
    )

    assert result == {keys[0]}
    estate_repository.get_used_object_keys.assert_called_once_with(
        session,
        keys,
    )
    user_repository.get_used_avatar_keys.assert_not_called()


def test_get_used_object_keys_uses_user_repository_for_avatars() -> None:
    service, estate_repository, user_repository = _service()
    session = Mock()
    keys = ["user-avatars/used.webp", "user-avatars/unused.webp"]
    user_repository.get_used_avatar_keys.return_value = {keys[0]}

    result = service.get_used_object_keys(
        session=session,
        purpose=MediaPurpose.user_avatar,
        object_keys=keys,
    )

    assert result == {keys[0]}
    user_repository.get_used_avatar_keys.assert_called_once_with(
        session,
        keys,
    )
    estate_repository.get_used_object_keys.assert_not_called()
