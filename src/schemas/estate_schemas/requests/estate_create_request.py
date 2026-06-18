from datetime import date, timedelta
from typing import Literal

from pydantic import ConfigDict, ValidationError, model_validator
from pydantic_core import InitErrorDetails

from domain.estate.enums.estate_listing_enums import ListingStatus
from schemas.estate_schemas.requests.estate_suggest_request import (
    EstateSuggestRequest,
)
from schemas.estate_schemas.validators_utils import make_value_error
from schemas.types import ID


class EstateCreateRequest(EstateSuggestRequest):
    model_config = ConfigDict(extra="forbid")

    seller_id: ID | None = None
    agent_id: ID | None = None
    expires_at: date | None = None
    listing_status: Literal[ListingStatus.draft, ListingStatus.active]

    @model_validator(mode="after")
    def validate_admin_creation_rules(self):
        errors: list[InitErrorDetails] = []

        self._validate_agent_and_status_compatibility(errors)
        self._validate_expires_at(errors)

        if errors:
            raise ValidationError.from_exception_data(
                title=type(self).__name__,
                line_errors=errors,
            )

        return self

    def _validate_agent_and_status_compatibility(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
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

    def _validate_expires_at(
        self,
        errors: list[InitErrorDetails],
    ) -> None:
        if (
            self.listing_status == ListingStatus.active
            and self.expires_at is None
        ):
            errors.append(
                make_value_error(
                    loc=("expires_at",),
                    message="expires_at is required when listing_status is active",
                    input_value=self.expires_at,
                )
            )
            return

        if self.expires_at is None:
            return

        if self.expires_at < date.today():
            errors.append(
                make_value_error(
                    loc=("expires_at",),
                    message="expires_at cannot be in the past",
                    input_value=self.expires_at,
                )
            )

        if self.expires_at < self.listing.available_from:
            errors.append(
                make_value_error(
                    loc=("expires_at",),
                    message="expires_at cannot be earlier than available_from",
                    input_value=self.expires_at,
                )
            )

        if self.expires_at > date.today() + timedelta(days=365):
            errors.append(
                make_value_error(
                    loc=("expires_at",),
                    message="expires_at must be less than 1 year ahead",
                    input_value=self.expires_at,
                )
            )
