import pytest

from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.user.user_model import User, UserRole
from security.password_crypto import PasswordCrypto
from tests.integration.conftest import ADMIN_ESTATE_PATH
from tests.integration.estate.test_filter_estate import (
    assert_ok_filter_response,
    create_filter_estate,
)


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


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_filter_estates_returns_all_statuses_by_default(
    client,
    db_session,
    logged_in_user,
):
    active_id = create_filter_estate(
        db_session,
        title="Active apartment",
        status=ListingStatus.active,
        price="100000.00",
    )
    draft_id = create_filter_estate(
        db_session,
        title="Draft apartment",
        status=ListingStatus.draft,
        price="200000.00",
    )
    archived_id = create_filter_estate(
        db_session,
        title="Archived apartment",
        status=ListingStatus.archived,
        price="300000.00",
    )

    response = client.get(
        ADMIN_ESTATE_PATH,
        query_string={
            "sort_by": "price",
            "order": "asc",
        },
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=3)

    assert [item["id"] for item in data["items"]] == [
        str(active_id),
        str(draft_id),
        str(archived_id),
    ]


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_filter_estates_by_status(
    client,
    db_session,
    logged_in_user,
):
    create_filter_estate(
        db_session,
        title="Active apartment",
        status=ListingStatus.active,
        price="100000.00",
    )
    draft_id = create_filter_estate(
        db_session,
        title="Draft apartment",
        status=ListingStatus.draft,
        price="200000.00",
    )
    rejected_id = create_filter_estate(
        db_session,
        title="Rejected apartment",
        status=ListingStatus.rejected,
        price="300000.00",
    )

    response = client.get(
        ADMIN_ESTATE_PATH,
        query_string=[
            ("status", ListingStatus.draft.value),
            ("status", ListingStatus.rejected.value),
            ("sort_by", "price"),
            ("order", "asc"),
        ],
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=2)

    assert [item["id"] for item in data["items"]] == [
        str(draft_id),
        str(rejected_id),
    ]


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_filter_estates_by_seller_id(
    client,
    db_session,
    logged_in_user,
):
    seller_a = _create_test_user(
        db_session,
        email="seller_a@example.com",
    )
    seller_b = _create_test_user(
        db_session,
        email="seller_b@example.com",
    )

    seller_a_first_id = create_filter_estate(
        db_session,
        title="Seller A first apartment",
        status=ListingStatus.suggested,
        price="100000.00",
        seller_id=seller_a.id,
    )
    seller_a_second_id = create_filter_estate(
        db_session,
        title="Seller A second apartment",
        status=ListingStatus.draft,
        price="200000.00",
        seller_id=seller_a.id,
    )
    create_filter_estate(
        db_session,
        title="Seller B apartment",
        status=ListingStatus.suggested,
        price="300000.00",
        seller_id=seller_b.id,
    )

    response = client.get(
        ADMIN_ESTATE_PATH,
        query_string={
            "seller_id": str(seller_a.id),
            "sort_by": "price",
            "order": "asc",
        },
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=2)

    assert [item["id"] for item in data["items"]] == [
        str(seller_a_first_id),
        str(seller_a_second_id),
    ]


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_admin_filter_estates_by_seller_status_and_public_filter(
    client,
    db_session,
    logged_in_user,
):
    seller_a = _create_test_user(
        db_session,
        email="combo_seller_a@example.com",
    )
    seller_b = _create_test_user(
        db_session,
        email="combo_seller_b@example.com",
    )

    matching_id = create_filter_estate(
        db_session,
        title="Matching suggested apartment",
        status=ListingStatus.suggested,
        price="120000.00",
        seller_id=seller_a.id,
    )
    create_filter_estate(
        db_session,
        title="Same seller but draft apartment",
        status=ListingStatus.draft,
        price="130000.00",
        seller_id=seller_a.id,
    )
    create_filter_estate(
        db_session,
        title="Same seller but too expensive apartment",
        status=ListingStatus.suggested,
        price="250000.00",
        seller_id=seller_a.id,
    )
    create_filter_estate(
        db_session,
        title="Other seller suggested apartment",
        status=ListingStatus.suggested,
        price="110000.00",
        seller_id=seller_b.id,
    )

    response = client.get(
        ADMIN_ESTATE_PATH,
        query_string={
            "seller_id": str(seller_a.id),
            "status": ListingStatus.suggested.value,
            "price_to": "150000.00",
        },
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=1)

    assert data["items"][0]["id"] == str(matching_id)


@pytest.mark.parametrize(
    "logged_in_user",
    [UserRole.user, UserRole.agent],
    indirect=True,
)
def test_admin_filter_estates_forbidden_for_non_admin(
    client,
    logged_in_user,
):
    response = client.get(
        ADMIN_ESTATE_PATH,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 403

    body = response.get_json()
    assert body["error"]["code"] == "forbidden"


def test_admin_filter_estates_unauthorized_without_token(client):
    response = client.get(ADMIN_ESTATE_PATH)

    assert response.status_code == 401
