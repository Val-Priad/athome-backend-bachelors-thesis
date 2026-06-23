from datetime import date, timedelta

from pydantic_core import InitErrorDetails

from domain.estate.enums.estate_listing_enums import ListingStatus
from schemas.estate_schemas.sections.listing_section import (
    EstateListingSection,
)
from schemas.estate_schemas.validators_utils import make_value_error
from schemas.types import ID


def validate_listing_mutation_rules(
    *,
    errors: list[InitErrorDetails],
    agent_id: ID | None,
    listing_status: ListingStatus,
    expires_at: date | None,
    listing: EstateListingSection,
) -> None:
    _validate_agent_and_status_compatibility(
        errors=errors,
        agent_id=agent_id,
        listing_status=listing_status,
    )

    _validate_expires_at(
        errors=errors,
        listing_status=listing_status,
        expires_at=expires_at,
        available_from=listing.available_from,
    )


def _validate_agent_and_status_compatibility(
    *,
    errors: list[InitErrorDetails],
    agent_id: ID | None,
    listing_status: ListingStatus,
) -> None:
    if agent_id is not None:
        return

    if listing_status != ListingStatus.active:
        return

    errors.append(
        make_value_error(
            loc=("agent_id",),
            message="agent_id is required when listing_status is active",
            input_value=agent_id,
        )
    )


def _validate_expires_at(
    *,
    errors: list[InitErrorDetails],
    listing_status: ListingStatus,
    expires_at: date | None,
    available_from: date,
) -> None:
    if listing_status == ListingStatus.active and expires_at is None:
        errors.append(
            make_value_error(
                loc=("expires_at",),
                message="expires_at is required when listing_status is active",
                input_value=expires_at,
            )
        )
        return

    if expires_at is None:
        return

    if expires_at < date.today():
        errors.append(
            make_value_error(
                loc=("expires_at",),
                message="expires_at cannot be in the past",
                input_value=expires_at,
            )
        )

    if expires_at < available_from:
        errors.append(
            make_value_error(
                loc=("expires_at",),
                message="expires_at cannot be earlier than available_from",
                input_value=expires_at,
            )
        )

    if expires_at > date.today() + timedelta(days=365):
        errors.append(
            make_value_error(
                loc=("expires_at",),
                message="expires_at must be less than 1 year ahead",
                input_value=expires_at,
            )
        )
