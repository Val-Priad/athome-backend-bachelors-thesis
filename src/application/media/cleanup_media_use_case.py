from uuid import UUID

from application.ports.object_storage import (
    ObjectStorageError,
    ObjectStorageProtocol,
)
from application.ports.transaction_manager import TransactionManagerProtocol
from domain.media.media_service import MediaService
from domain.media.media_usage_service import MediaUsageService
from exceptions.custom_exceptions.media_exceptions import MediaUploadError
from schemas.media_schemas.requests.media_cleanup_request import (
    MediaCleanupRequest,
)


class CleanupMediaUseCase:
    def __init__(
        self,
        *,
        transactions: TransactionManagerProtocol,
        media_service: MediaService,
        media_usage_service: MediaUsageService,
        object_storage: ObjectStorageProtocol,
    ) -> None:
        self._transactions = transactions
        self._media_service = media_service
        self._media_usage_service = media_usage_service
        self._object_storage = object_storage

    def execute(
        self,
        data: MediaCleanupRequest,
        requester_id: UUID,
    ) -> None:
        for object_key in data.object_keys:
            self._media_service.validate_owned_object_key(
                object_key=object_key,
                uploader_id=requester_id,
                purpose=data.purpose,
            )

        with self._transactions.session() as session:
            self._media_usage_service.ensure_object_keys_unused(
                session=session,
                purpose=data.purpose,
                object_keys=data.object_keys,
            )

        try:
            self._object_storage.delete_objects(data.object_keys)
        except ObjectStorageError as error:
            raise MediaUploadError() from error
