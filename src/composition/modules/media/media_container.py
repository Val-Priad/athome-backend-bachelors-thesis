from dataclasses import dataclass

from application.media.cleanup_media_use_case import CleanupMediaUseCase
from application.media.create_media_upload_url_use_case import (
    CreateMediaUploadUrlUseCase,
)


@dataclass(frozen=True, slots=True)
class MediaContainer:
    create_upload_url: CreateMediaUploadUrlUseCase
    cleanup: CleanupMediaUseCase
