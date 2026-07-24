import logging
from uuid import UUID

from application.ports.object_storage import (
    ObjectStorageError,
    ObjectStorageProtocol,
)
from application.ports.transaction_manager import TransactionManagerProtocol
from domain.estate.estate_repository import EstateRepository
from domain.user.services.authorization import AuthorizationService
from domain.user.user_model import UserRole

logger = logging.getLogger(__name__)


class DeleteEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_repository: EstateRepository,
        authorization_service: AuthorizationService,
        object_storage: ObjectStorageProtocol,
    ) -> None:
        self._transactions = transactions
        self._estate_repository = estate_repository
        self._authorization_service = authorization_service
        self._object_storage = object_storage

    def execute(self, estate_id: UUID, requester_id: UUID) -> None:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            object_keys = self._estate_repository.delete_estate_by_id(
                session,
                estate_id,
            )

        if object_keys:
            try:
                self._object_storage.delete_objects(list(object_keys))
            except ObjectStorageError:
                logger.exception(
                    "Failed to delete estate media objects",
                    extra={
                        "estate_id": str(estate_id),
                        "object_keys": list(object_keys),
                    },
                )
