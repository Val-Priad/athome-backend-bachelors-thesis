from application.transactions import TransactionManagerProtocol
from domain.estate.estate_service import EstateService
from schemas.estate_schemas.responses.estate_filter_response import (
    EstateFilterResponse,
)


class GetFilteredEstateUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        estate_service: EstateService,
    ) -> None:
        self._transactions = transactions
        self._estate_service = estate_service

    def execute(self, filters, requester_id) -> EstateFilterResponse:
        with self._transactions.session() as session:
            return self._estate_service.get_filtered_estate(
                session, filters, requester_id
            )
