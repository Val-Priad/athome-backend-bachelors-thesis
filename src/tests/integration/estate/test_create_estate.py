from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy import select

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.enums.estate_vicinity_enums import VicinityType
from domain.estate.estate_model import Estate
from domain.user.user_model import UserRole
from tests.integration.conftest import API_PREFIX, ESTATE_PATH


def base_payload(
    *,
    listing_status: ListingStatus = ListingStatus.draft,
    agent_id=None,
):
    future_date = date.today() + timedelta(days=1)
    expires_at = date.today() + timedelta(days=67)

    payload = {
        "estate_type": EstateType.apartment.value,
        "offer_type": OfferType.sale.value,
        "listing_status": listing_status.value,
        "expires_at": expires_at.isoformat(),
        "listing": {
            "available_from": future_date.isoformat(),
        },
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

    if agent_id is not None:
        payload["agent_id"] = str(agent_id)

    return payload


def get_created_estate(db_session, response) -> Estate:
    body = response.get_json()

    assert body["message"] == "OK"
    assert "data" in body
    assert "id" in body["data"]

    estate_id = UUID(body["data"]["id"])

    estate = db_session.scalar(select(Estate).where(Estate.id == estate_id))

    assert estate is not None
    return estate


@pytest.mark.parametrize(
    "listing_status",
    [
        ListingStatus.draft,
        ListingStatus.active,
    ],
)
@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_admin_create_estate_success(
    client,
    logged_in_user,
    any_user,
    db_session,
    listing_status,
):
    payload = base_payload(
        listing_status=listing_status,
        agent_id=any_user.id,
    )

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 201

    estate = get_created_estate(db_session, response)

    assert estate.estate_type == EstateType.apartment
    assert estate.offer_type == OfferType.sale
    assert estate.agent_id == any_user.id
    assert estate.seller_id is None

    assert estate.listing is not None
    assert estate.listing.status == listing_status
    assert estate.listing.expires_at is not None
    assert estate.listing.expires_at.date() == date.today() + timedelta(
        days=67
    )
    assert estate.listing.available_from == date.fromisoformat(
        payload["listing"]["available_from"]
    )

    if listing_status == ListingStatus.active:
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
    assert estate.details.usable_area == pytest.approx(48.5)

    assert estate.utilities is not None

    assert estate.apartment is not None
    assert estate.apartment.apartment_layout.value == "two_plus_one"
    assert estate.house is None

    assert len(estate.translations) == 1
    assert estate.translations[0].lang_code == "en"
    assert estate.translations[0].title == "Test apartment"

    assert len(estate.media) == 1
    assert estate.media[0].url == "https://example.com/image.jpg"
    assert estate.media[0].is_main is True

    assert len(estate.vicinities) == 2
    assert estate.vicinities[0].type == VicinityType.bus_stop
    assert estate.vicinities[0].name == "Test bus stop"
    assert estate.vicinities[0].distance_m == 157
    assert estate.vicinities[1].type == VicinityType.closest
    assert estate.vicinities[1].name == "Test bus stop"
    assert estate.vicinities[1].distance_m == 157


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_create_draft_estate_without_agent_success(
    client,
    logged_in_user,
    db_session,
):
    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=None,
    )

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 201

    estate = get_created_estate(db_session, response)

    assert estate.agent_id is None
    assert estate.listing is not None
    assert estate.listing.status == ListingStatus.draft
    assert estate.listing.published_at is None


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_create_active_estate_requires_agent(
    client,
    logged_in_user,
):
    payload = base_payload(
        listing_status=ListingStatus.active,
        agent_id=None,
    )

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["error"]["code"] == "request_validation_error"
    assert any(
        error["field"] == "agent_id"
        and "agent_id is required when listing_status is active"
        in error["message"]
        for error in body["error"].get("errors", [])
    )


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_admin_create_estate_rejects_past_available_from(
    client,
    logged_in_user,
    any_user,
):
    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=any_user.id,
    )
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


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
@pytest.mark.parametrize(
    "expires_at",
    [
        date.today().isoformat(),
        (date.today() + timedelta(days=368)).isoformat(),
    ],
)
def test_admin_create_estate_rejects_invalid_expires_at(
    client, logged_in_user, any_user, expires_at
):
    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=any_user.id,
    )

    payload["expires_at"] = expires_at

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["error"]["code"] == "request_validation_error"
    assert any(
        error["field"].endswith("expires_at")
        for error in body["error"].get("errors", [])
    )


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_admin_create_estate_rejects_active_estate_without_expires_field(
    client, logged_in_user, any_user
):
    payload = base_payload(
        listing_status=ListingStatus.active,
        agent_id=any_user.id,
    )
    payload["expires_at"] = None

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["error"]["code"] == "request_validation_error"
    assert any(
        error["field"].endswith("expires_at")
        for error in body["error"].get("errors", [])
    )


@pytest.mark.parametrize(
    "logged_in_user",
    [
        UserRole.user,
        UserRole.agent,
    ],
    indirect=True,
)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_create_estate_forbidden_for_non_admin(
    client,
    logged_in_user,
    any_user,
):
    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=any_user.id,
    )

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 403

    body = response.get_json()
    assert body["error"]["code"] == "forbidden"


@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_create_estate_unauthorized_without_token(client, any_user):
    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=any_user.id,
    )

    response = client.post(
        f"{API_PREFIX}{ESTATE_PATH}",
        json=payload,
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
