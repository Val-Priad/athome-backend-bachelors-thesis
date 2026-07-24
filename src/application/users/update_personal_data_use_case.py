from uuid import UUID

from application.ports.transaction_manager import TransactionManagerProtocol
from application.users.mapping.user_response_mapper import UserResponseMapper
from domain.media.media_enums import MediaPurpose, MediaType
from domain.media.media_service import MediaService
from domain.user.services.me_service import MeService
from schemas.me_schemas.me_requests import UpdateUserPersonalDataRequest
from schemas.me_schemas.me_responses import MeResponse


class UpdatePersonalDataUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        me_service: MeService,
        media_service: MediaService,
        response_mapper: UserResponseMapper,
    ) -> None:
        self._transactions = transactions
        self._me_service = me_service
        self._media_service = media_service
        self._response_mapper = response_mapper

    def execute(
        self, user_id: UUID, data: UpdateUserPersonalDataRequest
    ) -> MeResponse:
        updates = data.model_dump(exclude_unset=True)
        avatar_key = updates.get("avatar_key")

        if avatar_key is not None:
            self._media_service.validate_object(
                object_key=avatar_key,
                uploader_id=user_id,
                purpose=MediaPurpose.user_avatar,
                media_type=MediaType.image,
            )

        with self._transactions.session() as session:
            user = self._me_service.update_personal_data(
                session, user_id, updates
            )
            return self._response_mapper.to_response(MeResponse, user)
