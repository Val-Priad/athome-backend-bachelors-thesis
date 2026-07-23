from unittest.mock import Mock, patch

import pytest

from domain.estate.estate_media_repository import EstateMediaRepository
from exceptions.custom_exceptions.media_exceptions import (
    MediaObjectAlreadyUsedError,
)

OBJECT_KEY = "estate-media/uploader/media.webp"


def test_ensure_object_keys_unused_accepts_unused_keys() -> None:
    repository = EstateMediaRepository()
    session = Mock()

    with patch.object(
        repository,
        "get_used_object_keys",
        return_value=set(),
    ) as get_used_object_keys:
        repository.ensure_object_keys_unused(session, [OBJECT_KEY])

    get_used_object_keys.assert_called_once_with(session, [OBJECT_KEY])


def test_ensure_object_keys_unused_rejects_used_key() -> None:
    repository = EstateMediaRepository()

    with (
        patch.object(
            repository,
            "get_used_object_keys",
            return_value={OBJECT_KEY},
        ),
        pytest.raises(MediaObjectAlreadyUsedError),
    ):
        repository.ensure_object_keys_unused(Mock(), [OBJECT_KEY])
