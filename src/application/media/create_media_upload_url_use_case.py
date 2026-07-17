from collections.abc import Callable
from uuid import UUID, uuid4

from application.ports.object_storage import ObjectStorageProtocol
from schemas.media_schemas.requests.media_upload_url_request import (
    MediaUploadPurpose,
    MediaUploadUrlRequest,
)
from schemas.media_schemas.responses.presigned_upload_response import (
    PresignedUploadResponse,
)

PREFIX_BY_PURPOSE = {
    MediaUploadPurpose.estate: "estate-media",
    MediaUploadPurpose.user_avatar: "user-avatars",
}


class CreateMediaUploadUrlUseCase:
    def __init__(
        self,
        *,
        object_storage: ObjectStorageProtocol,
        presigned_url_ttl_seconds: int,
        uuid_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._object_storage = object_storage
        self._presigned_url_ttl_seconds = presigned_url_ttl_seconds
        self._uuid_factory = uuid_factory

    def execute(
        self,
        data: MediaUploadUrlRequest,
        requester_id: UUID,
    ) -> PresignedUploadResponse:
        object_key = (
            f"{PREFIX_BY_PURPOSE[data.purpose]}/{requester_id}/"
            f"{self._uuid_factory()}."
            f"{data.content_type.extension}"
        )
        upload_url = self._object_storage.create_upload_url(
            object_key=object_key,
            content_type=data.content_type.value,
        )

        return PresignedUploadResponse(
            upload_url=upload_url,
            object_key=object_key,
            expires_in=self._presigned_url_ttl_seconds,
        )
