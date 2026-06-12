import pytest
from sqlalchemy import select

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.estate_model import Estate
from domain.user.user_model import UserRole
from tests.integration.conftest import API_PREFIX, ESTATE_PATH


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_create_estate_draft_admin_success(client, logged_in_user, db_session):
    payload = {
        "estate_type": EstateType.apartment.value,
        "offer_type": OfferType.sale.value,
    }

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 201

    estate = db_session.scalar(
        select(Estate).where(
            Estate.estate_type == EstateType.apartment,
            Estate.offer_type == OfferType.sale,
        )
    )
    assert estate is not None

    assert estate.listing is not None
    assert estate.listing.status == ListingStatus.draft
    assert estate.listing.available_from is None

    assert estate.location is not None
    assert estate.pricing is not None
    assert estate.details is not None
    assert estate.utilities is not None
    assert estate.apartment is not None
    assert estate.house is not None
    assert estate.translations == []
    assert estate.media == []


def test_create_estate_draft_unauthorized_without_token(client):
    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json={
            "estate_type": EstateType.apartment.value,
            "offer_type": OfferType.sale.value,
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize("logged_in_user", [UserRole.user], indirect=True)
def test_create_estate_draft_forbidden_for_non_admin(client, logged_in_user):
    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json={
            "estate_type": EstateType.apartment.value,
            "offer_type": OfferType.sale.value,
        },
        headers=logged_in_user.headers,
    )

    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "forbidden"


@pytest.mark.parametrize(
    "logged_in_user",
    [UserRole.admin],
    indirect=True,
)
@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="missing required fields"),
        pytest.param(
            {"estate_type": "invalid", "offer_type": "sale"},
            id="invalid estate type",
        ),
        pytest.param(
            {"estate_type": "apartment", "offer_type": "invalid"},
            id="invalid offer type",
        ),
        pytest.param(
            {"estate_type": 1, "offer_type": 2},
            id="invalid types",
        ),
    ],
)
def test_create_estate_draft_validation_error(client, logged_in_user, payload):
    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "request_validation_error"
