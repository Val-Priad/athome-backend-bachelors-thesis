from collections.abc import Sequence

from sqlalchemy.orm import Session

from domain.estate.estate_media_repository import EstateMediaRepository
from domain.media.media_enums import MediaPurpose
from domain.user.user_repository import UserRepository


class MediaUsageService:
    def __init__(
        self,
        *,
        estate_media_repository: EstateMediaRepository,
        user_repository: UserRepository,
    ) -> None:
        self._estate_media_repository = estate_media_repository
        self._user_repository = user_repository

    def get_used_object_keys(
        self,
        *,
        session: Session,
        purpose: MediaPurpose,
        object_keys: Sequence[str],
    ) -> set[str]:
        if purpose == MediaPurpose.estate:
            return self._estate_media_repository.get_used_object_keys(
                session,
                list(object_keys),
            )

        if purpose == MediaPurpose.user_avatar:
            return self._user_repository.get_used_avatar_keys(
                session,
                object_keys,
            )

        raise ValueError(f"Unsupported media purpose: {purpose}")

    def ensure_object_keys_unused(
        self,
        *,
        session: Session,
        purpose: MediaPurpose,
        object_keys: Sequence[str],
    ) -> None:
        if purpose == MediaPurpose.estate:
            self._estate_media_repository.ensure_object_keys_unused(
                session,
                object_keys,
            )
            return

        if purpose == MediaPurpose.user_avatar:
            self._user_repository.ensure_avatar_keys_unused(
                session,
                object_keys,
            )
            return

        raise ValueError(f"Unsupported media purpose: {purpose}")
