from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.enums.estate_vicinity_enums import VicinityType
from domain.estate.estate_model import Estate
from domain.user.user_model import User, UserRole
from security.password_crypto import PasswordCrypto
from tests.integration.admin_estate.test_create_estate import base_payload
from tests.integration.conftest import ADMIN_ESTATE_PATH
from tests.integration.estate.test_filter_estate import create_filter_estate


def _create_test_user(
    db_session,
    *,
    email: str,
    role: UserRole = UserRole.user,
) -> User:
    user = User(
        email=email,
        password_hash=PasswordCrypto.hash_password("test_password"),
        is_email_verified=True,
        role=role,
    )
    db_session.add(user)
    db_session.flush()
    return user


def _get_estate(db_session, estate_id) -> Estate:
    estate = db_session.scalar(select(Estate).where(Estate.id == estate_id))
    assert estate is not None
    return estate


def _assert_ok_id_response(response, estate_id):
    assert response.status_code == 200

    body = response.get_json()
    assert body["message"] == "OK"
    assert body["data"]["id"] == str(estate_id)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_update_estate_success(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email="update_seller@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email="update_agent@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Old apartment",
        status=ListingStatus.draft,
        price="100000.00",
        seller_id=seller.id,
    )

    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)
    payload["offer_type"] = OfferType.lease
    payload["location"]["city"] = "Lviv"
    payload["location"]["street"] = "Updated Street"
    payload["location"]["house_number"] = "99B"
    payload["location"]["latitude"] = 49.8397
    payload["location"]["longitude"] = 24.0297
    payload["pricing"]["price"] = "77777.77"
    payload["details"]["usable_area"] = 64.5
    payload["apartment"]["apartment_layout"] = "three_plus_one"
    payload["translations"] = [
        {
            "lang_code": "en",
            "title": "Updated apartment",
            "description": "Updated apartment description",
        }
    ]
    payload["media"] = [
        {
            "object_key": "estate-media/updated-main.webp",
            "media_type": "image",
        }
    ]

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        json=payload,
        headers=logged_in_user.headers,
    )

    _assert_ok_id_response(response, estate_id)

    db_session.expire_all()

    estate = _get_estate(db_session, estate_id)

    assert estate.seller_id == seller.id
    assert estate.agent_id == agent.id
    assert estate.estate_type == EstateType.apartment
    assert estate.offer_type == OfferType.lease

    assert estate.listing.status == ListingStatus.draft
    assert estate.listing.published_at is None
    assert estate.listing.expires_at == date.today() + timedelta(days=67)
    assert estate.listing.available_from == date.fromisoformat(
        payload["listing"]["available_from"]
    )

    assert estate.location.city == "Lviv"
    assert estate.location.street == "Updated Street"
    assert estate.location.house_number == "99B"
    assert estate.location.latitude == pytest.approx(49.8397)
    assert estate.location.longitude == pytest.approx(24.0297)

    assert estate.pricing.price == Decimal("77777.77")
    assert estate.details.usable_area == pytest.approx(64.5)

    assert estate.utilities is not None

    assert estate.apartment is not None
    assert estate.apartment.apartment_layout.value == "three_plus_one"
    assert estate.house is None

    assert len(estate.translations) == 1
    assert estate.translations[0].lang_code == "en"
    assert estate.translations[0].title == "Updated apartment"

    assert len(estate.media) == 1
    assert estate.media[0].object_key == "estate-media/updated-main.webp"
    assert estate.media[0].position == 0

    assert len(estate.vicinities) == 2
    assert estate.vicinities[0].type == VicinityType.bus_stop
    assert estate.vicinities[0].name == "Test bus stop"
    assert estate.vicinities[0].distance_m == 157
    assert estate.vicinities[1].type == VicinityType.closest
    assert estate.vicinities[1].name == "Test bus stop"
    assert estate.vicinities[1].distance_m == 157


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_update_draft_to_active_sets_published_at(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email="active_update_seller@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email="active_update_agent@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Draft apartment",
        status=ListingStatus.draft,
        seller_id=seller.id,
    )

    payload = base_payload(
        listing_status=ListingStatus.active,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        json=payload,
        headers=logged_in_user.headers,
    )

    _assert_ok_id_response(response, estate_id)

    db_session.expire_all()

    estate = _get_estate(db_session, estate_id)

    assert estate.listing.status == ListingStatus.active
    assert estate.listing.published_at == date.today()
    assert estate.listing.expires_at == date.today() + timedelta(days=67)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_update_active_to_draft_clears_published_at(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email="draft_update_seller@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email="draft_update_agent@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Active apartment",
        status=ListingStatus.active,
        seller_id=seller.id,
        agent_id=agent.id,
    )

    estate_before_update = _get_estate(db_session, estate_id)
    assert estate_before_update.listing.published_at is not None

    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        json=payload,
        headers=logged_in_user.headers,
    )

    _assert_ok_id_response(response, estate_id)

    db_session.expire_all()

    estate = _get_estate(db_session, estate_id)

    assert estate.listing.status == ListingStatus.draft
    assert estate.listing.published_at is None


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_update_active_to_archived_keeps_published_at(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email="archive_update_seller@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email="archive_update_agent@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Active apartment",
        status=ListingStatus.active,
        seller_id=seller.id,
        agent_id=agent.id,
    )

    estate_before_update = _get_estate(db_session, estate_id)
    old_published_at = estate_before_update.listing.published_at
    assert old_published_at is not None

    payload = base_payload(
        listing_status=ListingStatus.archived,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        json=payload,
        headers=logged_in_user.headers,
    )

    _assert_ok_id_response(response, estate_id)

    db_session.expire_all()

    estate = _get_estate(db_session, estate_id)

    assert estate.listing.status == ListingStatus.archived
    assert estate.listing.published_at == old_published_at


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_update_estate_allows_past_available_from(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email="past_available_seller@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email="past_available_agent@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Old available apartment",
        status=ListingStatus.draft,
        seller_id=seller.id,
    )

    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)
    payload["listing"]["available_from"] = (
        date.today() - timedelta(days=30)
    ).isoformat()

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        json=payload,
        headers=logged_in_user.headers,
    )

    db_session.expire_all()

    _assert_ok_id_response(response, estate_id)

    estate = _get_estate(db_session, estate_id)

    assert estate.listing.available_from == date.today() - timedelta(days=30)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_update_active_estate_requires_agent(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email="requires_agent_seller@example.com",
        role=UserRole.user,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Draft apartment",
        status=ListingStatus.draft,
        seller_id=seller.id,
    )

    payload = base_payload(
        listing_status=ListingStatus.active,
        agent_id=None,
    )
    payload["seller_id"] = str(seller.id)

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
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
def test_admin_update_active_estate_requires_expires_at(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email="requires_expires_seller@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email="requires_expires_agent@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Draft apartment",
        status=ListingStatus.draft,
        seller_id=seller.id,
    )

    payload = base_payload(
        listing_status=ListingStatus.active,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)
    payload["expires_at"] = None

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
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
def test_admin_update_estate_rejects_invalid_expires_at(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email="invalid_expires_seller@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email="invalid_expires_agent@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Draft apartment",
        status=ListingStatus.draft,
        seller_id=seller.id,
    )

    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)
    payload["expires_at"] = (date.today() - timedelta(days=1)).isoformat()

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
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
    [UserRole.user, UserRole.agent],
    indirect=True,
)
def test_update_estate_forbidden_for_non_admin(
    client,
    db_session,
    logged_in_user,
):
    seller = _create_test_user(
        db_session,
        email=f"forbidden_seller_{logged_in_user.role.value}@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email=f"forbidden_agent_{logged_in_user.role.value}@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Forbidden update apartment",
        status=ListingStatus.draft,
        seller_id=seller.id,
    )

    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 403

    body = response.get_json()
    assert body["error"]["code"] == "forbidden"


def test_update_estate_unauthorized_without_token(
    client,
    db_session,
):
    seller = _create_test_user(
        db_session,
        email="unauthorized_update_seller@example.com",
        role=UserRole.user,
    )
    agent = _create_test_user(
        db_session,
        email="unauthorized_update_agent@example.com",
        role=UserRole.agent,
    )

    estate_id = create_filter_estate(
        db_session,
        title="Unauthorized update apartment",
        status=ListingStatus.draft,
        seller_id=seller.id,
    )

    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=agent.id,
    )
    payload["seller_id"] = str(seller.id)

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        json=payload,
    )

    assert response.status_code == 401


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_update_missing_estate_returns_404(
    client,
    logged_in_user,
):
    payload = base_payload(
        listing_status=ListingStatus.draft,
        agent_id=None,
    )

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{uuid4()}",
        json=payload,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["error"]["code"] == "estate_not_found"


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_update_estate_validation_error(
    client,
    db_session,
    logged_in_user,
):
    estate_id = create_filter_estate(
        db_session,
        title="Validation error apartment",
        status=ListingStatus.draft,
    )

    response = client.put(
        f"{ADMIN_ESTATE_PATH}/{estate_id}",
        json={},
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "request_validation_error"
