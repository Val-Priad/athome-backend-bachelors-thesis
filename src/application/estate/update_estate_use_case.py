import logging
from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.estate.estate_participants_service import EstateParticipantsService
from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from infrastructure.object_storage.object_storage_protocol import (
    ObjectStorageProtocol,
)
from schemas.estate_schemas.requests.estate_update_request import (
    EstateUpdateRequest,
)
from schemas.estate_schemas.responses.estate_create_response import (
    EstateIDResponse,
)
from security.authorization import AuthorizationService

logger = logging.getLogger(__name__)


class UpdateEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
        participants_service: EstateParticipantsService,
        object_storage: ObjectStorageProtocol,
    ) -> None:
        self._transactions = transactions
        self._estate_service = estate_service
        self._authorization_service = authorization_service
        self._participants_service = participants_service
        self._object_storage = object_storage

    def execute(
        self,
        estate_id: UUID,
        data: EstateUpdateRequest,
        requester_id: UUID,
    ) -> EstateIDResponse:
        with self._transactions.session() as session:
            self._authorization_service.ensure_has_rights(
                session, requester_id, UserRole.admin
            )
            self._participants_service.check_participants(session, data)
            estate, removed_object_keys = self._estate_service.update_estate(
                session=session,
                estate_id=estate_id,
                data=data,
            )
            response = EstateIDResponse.from_model(estate)

        if removed_object_keys:
            try:
                self._object_storage.delete_objects(removed_object_keys)
            except Exception:
                logger.exception(
                    "Failed to delete removed estate media objects",
                    extra={
                        "estate_id": str(estate_id),
                        "object_keys": list(removed_object_keys),
                    },
                )

        return response
