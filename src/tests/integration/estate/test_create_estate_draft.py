from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.enums.estate_vicinity_enums import VicinityType
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
    assert response.get_json() == {"message": "OK"}

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
    assert estate.vicinities == []
    assert estate.translations == []
    assert estate.media == []


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_create_estate_draft_persists_partial_payload(
    client, logged_in_user, db_session
):
    future_date = date.today() + timedelta(days=1)
    payload = {
        "estate_type": EstateType.apartment.value,
        "offer_type": OfferType.sale.value,
        "location": {
            "city": "Kyiv",
            "street": "Step",
            "house_number": "12A",
            "latitude": 52.2297,
            "longitude": 21.0122,
        },
        "pricing": {"price": "123456.78"},
        "listing": {
            "status": ListingStatus.draft.value,
            "available_from": future_date.isoformat(),
        },
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
    assert estate.listing.available_from == future_date

    assert estate.location is not None
    assert estate.location.city == "Kyiv"
    assert estate.location.street == "Step"
    assert estate.location.house_number == "12A"
    assert estate.location.latitude == pytest.approx(52.2297)
    assert estate.location.longitude == pytest.approx(21.0122)

    assert estate.pricing is not None
    assert estate.pricing.price == Decimal("123456.78")

    assert estate.details is not None
    assert estate.utilities is not None
    assert estate.apartment is not None
    assert estate.house is not None
    assert len(estate.vicinities) == 2
    assert estate.vicinities[0].type == VicinityType.bus_stop
    assert estate.vicinities[0].name == "Test bus stop"
    assert estate.vicinities[0].distance_m == 157
    assert estate.vicinities[1].type == VicinityType.closest
    assert estate.vicinities[1].name == "Test bus stop"
    assert estate.vicinities[1].distance_m == 157


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_create_estate_draft_rejects_past_available_from(
    client, logged_in_user
):
    payload = {
        "estate_type": EstateType.apartment.value,
        "offer_type": OfferType.sale.value,
        "listing": {
            "status": ListingStatus.draft.value,
            "available_from": (date.today() - timedelta(days=1)).isoformat(),
        },
    }

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"]["code"] == "request_validation_error"
    assert any(
        error["field"].endswith("available_from")
        and "cannot be in the past" in error["message"]
        for error in body["error"].get("errors", [])
    )


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
