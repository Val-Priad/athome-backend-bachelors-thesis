from datetime import date

from domain.estate.enums.estate_listing_enums import ListingStatus
from schemas.estate_schemas.requests.estate_suggest_request import (
    EstateSuggestRequest,
)
from schemas.types import ID


class EstateMutationType(EstateSuggestRequest):
    seller_id: ID | None = None
    agent_id: ID | None = None
    expires_at: date | None = None
    listing_status: ListingStatus
