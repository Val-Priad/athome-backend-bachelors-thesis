from uuid import UUID

from sqlalchemy.orm import Session

from application.ports.transaction_manager import TransactionManagerProtocol
from domain.estate.estate_media_repository import EstateMediaRepository
from domain.estate.estate_participants_service import EstateParticipantsService
from domain.estate.estate_repository import EstateRepository
from domain.estate.estate_service import EstateService
from domain.media.media_enums import MediaPurpose
from domain.media.media_service import MediaService
from domain.user.services.authorization import AuthorizationService
from domain.user.user_model import UserRole
from schemas.estate_schemas.requests.estate_update_request import (
    EstateUpdateRequest,
)
from schemas.estate_schemas.responses.estate_create_response import (
    EstateIDResponse,
)


class UpdateEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
        participants_service: EstateParticipantsService,
        media_service: MediaService,
        estate_media_repository: EstateMediaRepository,
        estate_repository: EstateRepository,
    ) -> None:
        self._transactions = transactions
        self._estate_service = estate_service
        self._authorization_service = authorization_service
        self._participants_service = participants_service
        self._media_service = media_service
        self._estate_media_repository = estate_media_repository
        self._estate_repository = estate_repository

    def execute(
        self,
        estate_id: UUID,
        data: EstateUpdateRequest,
        requester_id: UUID,
    ) -> EstateIDResponse:
        with self._transactions.session() as session:
            self._ensure_rights_and_data_validity(
                session,
                requester_id,
                data,
            )
            estate = self._estate_repository.get_full_estate_by_id(
                session,
                estate_id,
            )
            current_object_keys = {item.object_key for item in estate.media}

        added_media = [
            item
            for item in data.media
            if item.object_key not in current_object_keys
        ]
        self._media_service.validate_objects(
            media=added_media,
            uploader_id=requester_id,
            purpose=MediaPurpose.estate,
        )

        with self._transactions.session() as session:
            self._ensure_rights_and_data_validity(
                session,
                requester_id,
                data,
            )
            self._estate_media_repository.ensure_object_keys_unused(
                session,
                [item.object_key for item in added_media],
            )
            estate = self._estate_service.update_estate(
                session=session,
                estate_id=estate_id,
                data=data,
            )
            return EstateIDResponse.from_model(estate)

    def _ensure_rights_and_data_validity(
        self,
        session: Session,
        requester_id: UUID,
        data: EstateUpdateRequest,
    ) -> None:
        self._authorization_service.ensure_has_rights(
            session,
            requester_id,
            UserRole.admin,
        )
        self._participants_service.check_participants(session, data)
