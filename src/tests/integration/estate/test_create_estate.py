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


def _base_payload(broker_id):
    return {
        "estate_type": EstateType.apartment.value,
        "offer_type": OfferType.sale.value,
        "broker_id": str(broker_id),
        "listing": {},
        "location": {
            "region": "kyiv_city",
            "city": "Kyiv",
            "street": "Step",
            "house_number": "12A",
            "latitude": 52.2297,
            "longitude": 21.0122,
        },
        "pricing": {
            "price": "123456.78",
            "price_unit": "per_property",
        },
        "details": {
            "usable_area": 48.5,
        },
        "apartment": {
            "apartment_layout": "two_plus_one",
        },
        "translations": [
            {
                "lang_code": "en",
                "title": "Test apartment",
                "description": "Test apartment description",
            }
        ],
        "media": [
            {
                "url": "https://example.com/image.jpg",
                "media_type": "image",
                "is_main": True,
            }
        ],
    }


@pytest.mark.parametrize(
    "logged_in_user, expected_status",
    [
        (UserRole.admin, ListingStatus.active),
        (UserRole.user, ListingStatus.suggested),
        (UserRole.agent, ListingStatus.suggested),
    ],
    indirect=["logged_in_user"],
)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_create_estate_success(
    client, logged_in_user, any_user, db_session, expected_status
):
    payload = _base_payload(any_user.id)

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
            Estate.broker_id == any_user.id,
        )
    )
    assert estate is not None

    assert estate.listing is not None
    assert estate.listing.status == expected_status
    assert estate.listing.available_from is None
    if expected_status == ListingStatus.active:
        assert estate.listing.published_at is not None
    else:
        assert estate.listing.published_at is None

    assert estate.location is not None
    assert estate.location.city == "Kyiv"
    assert estate.location.street == "Step"
    assert estate.location.house_number == "12A"
    assert estate.location.latitude == pytest.approx(52.2297)
    assert estate.location.longitude == pytest.approx(21.0122)

    assert estate.pricing is not None
    assert estate.pricing.price == Decimal("123456.78")

    assert estate.details is not None
    assert estate.utilities is None
    assert estate.apartment is not None
    assert estate.house is None
    assert len(estate.vicinities) == 2
    assert estate.vicinities[0].type == VicinityType.bus_stop
    assert estate.vicinities[0].name == "Test bus stop"
    assert estate.vicinities[0].distance_m == 157
    assert estate.vicinities[1].type == VicinityType.closest
    assert estate.vicinities[1].name == "Test bus stop"
    assert estate.vicinities[1].distance_m == 157


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_create_estate_persists_available_from(
    client, logged_in_user, any_user, db_session
):
    future_date = date.today() + timedelta(days=1)
    payload = _base_payload(any_user.id)
    payload["listing"] = {"available_from": future_date.isoformat()}

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
            Estate.broker_id == any_user.id,
        )
    )
    assert estate is not None
    assert estate.listing is not None
    assert estate.listing.available_from == future_date


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_create_estate_rejects_past_available_from(
    client, logged_in_user, any_user
):
    payload = _base_payload(any_user.id)
    payload["listing"] = {
        "available_from": (date.today() - timedelta(days=1)).isoformat(),
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


@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_create_estate_unauthorized_without_token(client, any_user):
    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=_base_payload(any_user.id),
    )

    assert response.status_code == 401


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_create_estate_validation_error(client, logged_in_user):
    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json={},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "request_validation_error"
