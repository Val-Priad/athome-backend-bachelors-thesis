from collections.abc import Sequence
from pathlib import PurePosixPath
from typing import Protocol
from uuid import UUID

from application.ports.object_storage import (
    ObjectStorageError,
    ObjectStorageProtocol,
)
from domain.media.media_config import (
    MEDIA_CONFIG_BY_PURPOSE,
    MediaPurposeConfig,
)
from domain.media.media_enums import MediaPurpose, MediaType
from exceptions.custom_exceptions.media_exceptions import (
    InvalidMediaObjectKeyError,
    MediaObjectNotFoundError,
    MediaUploadError,
)


class MediaItemProtocol(Protocol):
    object_key: str
    media_type: MediaType


class MediaService:
    def __init__(self, object_storage: ObjectStorageProtocol) -> None:
        self._object_storage = object_storage

    def validate_object(
        self,
        *,
        object_key: str,
        uploader_id: UUID,
        purpose: MediaPurpose,
        media_type: MediaType,
    ) -> None:
        self.validate_owned_object_key(
            object_key=object_key,
            uploader_id=uploader_id,
            purpose=purpose,
            media_type=media_type,
        )
        self._ensure_object_exists(object_key)

    def validate_owned_object_key(
        self,
        *,
        object_key: str,
        uploader_id: UUID,
        purpose: MediaPurpose,
        media_type: MediaType | None = None,
    ) -> None:
        config = MEDIA_CONFIG_BY_PURPOSE[purpose]
        filename = self._extract_filename(
            object_key=object_key,
            uploader_id=uploader_id,
            config=config,
        )
        extension = self._validate_generated_filename(filename)
        if media_type is None:
            allowed_extensions = {
                allowed_extension
                for extensions in config.extensions_by_media_type.values()
                for allowed_extension in extensions
            }
            if extension not in allowed_extensions:
                raise InvalidMediaObjectKeyError()
        else:
            self._validate_extension(
                extension=extension,
                media_type=media_type,
                config=config,
            )

    def validate_objects(
        self,
        *,
        media: Sequence[MediaItemProtocol],
        uploader_id: UUID,
        purpose: MediaPurpose,
    ) -> None:
        for item in media:
            self.validate_object(
                object_key=item.object_key,
                uploader_id=uploader_id,
                purpose=purpose,
                media_type=item.media_type,
            )

    @staticmethod
    def _extract_filename(
        *,
        object_key: str,
        uploader_id: UUID,
        config: MediaPurposeConfig,
    ) -> str:
        uploader_prefix = f"{config.prefix}/{uploader_id}/"
        if not object_key.startswith(uploader_prefix):
            raise InvalidMediaObjectKeyError()

        filename = object_key.removeprefix(uploader_prefix)
        if "/" in filename:
            raise InvalidMediaObjectKeyError()

        return filename

    @staticmethod
    def _validate_generated_filename(filename: str) -> str:
        path = PurePosixPath(filename)
        if not path.stem or not path.suffix:
            raise InvalidMediaObjectKeyError()

        try:
            media_id = UUID(path.stem)
        except ValueError as error:
            raise InvalidMediaObjectKeyError() from error

        if str(media_id) != path.stem:
            raise InvalidMediaObjectKeyError()

        return path.suffix.removeprefix(".")

    @staticmethod
    def _validate_extension(
        *,
        extension: str,
        media_type: MediaType,
        config: MediaPurposeConfig,
    ) -> None:
        allowed_extensions = config.extensions_by_media_type.get(media_type)
        if allowed_extensions is None or extension not in allowed_extensions:
            raise InvalidMediaObjectKeyError()

    def _ensure_object_exists(self, object_key: str) -> None:
        try:
            object_exists = self._object_storage.object_exists(object_key)
        except ObjectStorageError as error:
            raise MediaUploadError() from error

        if not object_exists:
            raise MediaObjectNotFoundError()
