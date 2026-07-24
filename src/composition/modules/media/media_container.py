from dataclasses import dataclass

from application.media.cleanup_orphaned_media_use_case import (
    CleanupOrphanedMediaUseCase,
)
from application.media.create_media_upload_url_use_case import (
    CreateMediaUploadUrlUseCase,
)


@dataclass(frozen=True, slots=True)
class MediaContainer:
    create_upload_url: CreateMediaUploadUrlUseCase
    cleanup_orphans: CleanupOrphanedMediaUseCase
