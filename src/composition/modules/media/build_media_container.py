from datetime import timedelta

from application.media.cleanup_media_use_case import CleanupMediaUseCase
from application.media.cleanup_orphaned_media_use_case import (
    CleanupOrphanedMediaUseCase,
)
from application.media.create_media_upload_url_use_case import (
    CreateMediaUploadUrlUseCase,
)
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from composition.modules.media.media_container import MediaContainer
from composition.services.service_container import ServiceContainer


def build_media_container(
    *,
    infrastructure: InfrastructureContainer,
    services: ServiceContainer,
    presigned_url_ttl_seconds: int,
    media_orphan_min_age_hours: int,
) -> MediaContainer:
    return MediaContainer(
        create_upload_url=CreateMediaUploadUrlUseCase(
            object_storage=infrastructure.object_storage,
            presigned_url_ttl_seconds=presigned_url_ttl_seconds,
        ),
        cleanup=CleanupMediaUseCase(
            transactions=infrastructure.transactions,
            media_service=services.media,
            media_usage_service=services.media_usage,
            object_storage=infrastructure.object_storage,
        ),
        cleanup_orphans=CleanupOrphanedMediaUseCase(
            transactions=infrastructure.transactions,
            media_usage_service=services.media_usage,
            object_storage=infrastructure.object_storage,
            min_object_age=timedelta(
                hours=media_orphan_min_age_hours,
            ),
        ),
    )
