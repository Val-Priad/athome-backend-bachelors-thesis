from uuid import UUID

from sqlalchemy.orm import Session

from application.ports.transaction_manager import TransactionManagerProtocol
from domain.estate.estate_participants_service import EstateParticipantsService
from domain.estate.estate_service import EstateService
from domain.user.user_model import UserRole
from schemas.estate_schemas.requests.estate_create_request import (
    EstateCreateRequest,
)
from schemas.estate_schemas.requests.estate_create_type import (
    EstateMutationType,
)
from schemas.estate_schemas.responses.estate_create_response import (
    EstateIDResponse,
)
from security.authorization import AuthorizationService


class CreateEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_service: EstateService,
        authorization_service: AuthorizationService,
        participants_service: EstateParticipantsService,
    ) -> None:
        self._transactions = transactions
        self._estate_service = estate_service
        self._authorization_service = authorization_service
        self._participants_service = participants_service

    def execute(
        self,
        data: EstateCreateRequest,
        requester_id: UUID,
    ) -> EstateIDResponse:
        creation_data = EstateMutationType(**data.model_dump())

        with self._transactions.session() as session:
            self._ensure_rights_and_data_validity(session, requester_id, data)

        vicinities = self._estate_service.get_vicinities_or_empty(
            data.location
        )

        with self._transactions.session() as session:
            self._ensure_rights_and_data_validity(session, requester_id, data)
            estate = self._estate_service.create_estate(
                session, creation_data, vicinities
            )
            return EstateIDResponse(id=estate.id)

    def _ensure_rights_and_data_validity(
        self,
        session: Session,
        requester_id: UUID,
        data: EstateCreateRequest,
    ) -> None:
        self._authorization_service.ensure_has_rights(
            session, requester_id, UserRole.admin
        )
        self._participants_service.check_participants(session, data)
