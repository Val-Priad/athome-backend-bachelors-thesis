from application.media.create_media_upload_url_use_case import (
    CreateMediaUploadUrlUseCase,
)
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from composition.modules.media.media_container import MediaContainer


def build_media_container(
    *,
    infrastructure: InfrastructureContainer,
    presigned_url_ttl_seconds: int,
) -> MediaContainer:
    return MediaContainer(
        create_upload_url=CreateMediaUploadUrlUseCase(
            object_storage=infrastructure.object_storage,
            presigned_url_ttl_seconds=presigned_url_ttl_seconds,
        )
    )
