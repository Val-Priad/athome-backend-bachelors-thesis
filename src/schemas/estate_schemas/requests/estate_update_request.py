from datetime import date
from typing import Literal

from pydantic import ConfigDict, ValidationError, model_validator
from pydantic_core import InitErrorDetails
from typing_extensions import override

from domain.estate.enums.estate_listing_enums import ListingStatus
from schemas.estate_schemas.requests.estate_listing_validation import (
    validate_listing_mutation_rules,
)
from schemas.estate_schemas.requests.estate_suggest_request import (
    EstateSuggestRequest,
)
from schemas.types import ID


class EstateUpdateRequest(EstateSuggestRequest):
    model_config = ConfigDict(extra="forbid")

    seller_id: ID | None = None
    agent_id: ID | None = None
    expires_at: date | None = None
    listing_status: Literal[
        ListingStatus.draft,
        ListingStatus.active,
        ListingStatus.archived,
    ]

    @model_validator(mode="after")
    def validate_update_rules(self):
        errors: list[InitErrorDetails] = []

        validate_listing_mutation_rules(
            errors=errors,
            agent_id=self.agent_id,
            listing_status=self.listing_status,
            expires_at=self.expires_at,
            listing=self.listing,
        )

        if errors:
            raise ValidationError.from_exception_data(
                title=type(self).__name__,
                line_errors=errors,
            )

        return self

    @override
    def _validate_available_from(self, errors):
        return
