from uuid import UUID

from application.transactions import TransactionManagerProtocol
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.estate_repository import EstateRepository
from domain.user.user_model import UserRole
from exceptions.custom_exceptions.estate_exceptions import EstateNotFoundError
from schemas.estate_schemas.responses.estate_get_response import (
    EstateGeneralGetResponse,
    EstateGetResponseWithSeller,
)
from security.authorization import AuthorizationService


class GetEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_repository: EstateRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._transactions = transactions
        self._estate_repository = estate_repository
        self._authorization_service = authorization_service

    def execute(
        self, requester_id: UUID | None, id: UUID
    ) -> EstateGeneralGetResponse | EstateGetResponseWithSeller:
        with self._transactions.session() as session:
            estate = self._estate_repository.get_full_estate_by_id(session, id)

            requester_is_staff = bool(
                requester_id
                and self._authorization_service.users_role_is(
                    session, requester_id, UserRole.admin, UserRole.agent
                )
            )

            if (
                not requester_is_staff
                and estate.listing.status != ListingStatus.active
            ):
                raise EstateNotFoundError()

            if requester_is_staff:
                return EstateGetResponseWithSeller.from_model(estate)

            return EstateGeneralGetResponse.from_model(estate)
