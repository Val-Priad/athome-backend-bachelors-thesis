from typing import Literal

from pydantic import ConfigDict, ValidationError, model_validator
from pydantic_core import InitErrorDetails

from domain.estate.enums.estate_listing_enums import ListingStatus
from schemas.estate_schemas.estate_suggest_request import EstateSuggestRequest
from schemas.estate_schemas.validators_utils import make_value_error
from schemas.types import ID


class EstateCreateRequest(EstateSuggestRequest):
    model_config = ConfigDict(extra="forbid")

    seller_id: ID | None = None
    agent_id: ID | None = None
    listing_status: Literal[ListingStatus.draft, ListingStatus.active]

    @model_validator(mode="after")
    def validate_agent_and_status_compatibility(self):
        errors: list[InitErrorDetails] = []
        if (
            self.agent_id is None
            and self.listing_status == ListingStatus.active
        ):
            errors.append(
                make_value_error(
                    loc=("agent_id",),
                    message="agent_id is required when listing_status is active",
                    input_value=self.agent_id,
                )
            )

        if errors:
            raise ValidationError.from_exception_data(
                title=type(self).__name__,
                line_errors=errors,
            )

        return self
