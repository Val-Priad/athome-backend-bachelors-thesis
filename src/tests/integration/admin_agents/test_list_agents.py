import datetime

import pytest

from domain.estate.enums.estate_enums import EstateType, OfferType
from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.estate.estate_model import Estate
from domain.estate.models.estate_listing_model import EstateListing
from domain.user.user_model import User, UserRole
from schemas.admin_schemas.admin_users_schemas.admin_agent_response import (
    AgentsListItem,
)
from security.password_crypto import PasswordCrypto
from tests.integration.conftest import API_PREFIX

ADMIN_AGENTS_PATH = "/admin/agents"


@pytest.fixture
def populate_agents(db_session):
    for i in range(37):
        db_session.add(
            User(
                email=f"agent_{i:02d}@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.agent,
                name=f"Agent {i:02d}",
                phone_number=f"+4207012345{i:02d}",
                avatar_key=f"avatars/agents/agent_{i}.png",
            )
        )

    for i in range(5):
        db_session.add(
            User(
                email=f"user_{i}@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
            )
        )

    for i in range(3):
        db_session.add(
            User(
                email=f"admin_{i}@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.admin,
            )
        )

    db_session.flush()


def _create_agent(
    db_session,
    *,
    email: str,
    name: str | None = None,
    phone_number: str | None = None,
    created_at: datetime.datetime | None = None,
):
    agent = User(
        email=email,
        password_hash=PasswordCrypto.hash_password("any_password"),
        is_email_verified=True,
        role=UserRole.agent,
        name=name,
        phone_number=phone_number,
        created_at=created_at,
    )
    db_session.add(agent)
    db_session.flush()
    return agent


def _create_estate_for_agent(
    db_session,
    *,
    agent_id,
    status: ListingStatus,
):
    estate = Estate(
        agent_id=agent_id,
        estate_type=EstateType.apartment,
        offer_type=OfferType.sale,
        listing=EstateListing(
            status=status,
            available_from=datetime.date(2026, 1, 1),
            published_at=(
                datetime.datetime(
                    2026,
                    1,
                    1,
                    tzinfo=datetime.timezone.utc,
                )
                if status == ListingStatus.active
                else None
            ),
            expires_at=None,
        ),
    )
    db_session.add(estate)
    db_session.flush()
    return estate


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_success_defaults(
    client,
    logged_in_user,
    populate_agents,
):
    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    body = response.get_json()
    data = body["data"]

    assert data["total"] == 37
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) == 20

    first_item = data["items"][0]
    AgentsListItem.model_validate(first_item)

    assert set(first_item) == {
        "id",
        "email",
        "name",
        "phone_number",
        "avatar_key",
        "estate_qty",
        "created_at",
    }


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_supports_pagination(
    client,
    logged_in_user,
    populate_agents,
):
    response_page_1 = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}"
        "?page=1&page_size=15&sort_by=email&sort_order=asc",
        headers=logged_in_user.headers,
    )

    response_page_2 = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}"
        "?page=2&page_size=15&sort_by=email&sort_order=asc",
        headers=logged_in_user.headers,
    )

    assert response_page_1.status_code == 200
    assert response_page_2.status_code == 200

    emails_page_1 = {
        item["email"] for item in response_page_1.get_json()["data"]["items"]
    }
    emails_page_2 = {
        item["email"] for item in response_page_2.get_json()["data"]["items"]
    }

    assert emails_page_1.isdisjoint(emails_page_2)

    data = response_page_2.get_json()["data"]

    assert data["total"] == 37
    assert data["page"] == 2
    assert data["page_size"] == 15
    assert len(data["items"]) == 15

    emails = [item["email"] for item in data["items"]]
    assert emails == sorted(emails)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_filters_by_email(
    client,
    logged_in_user,
    db_session,
):
    _create_agent(
        db_session,
        email="target.agent.1@example.com",
        name="Agent One",
    )
    _create_agent(
        db_session,
        email="target.agent.2@example.com",
        name="Agent Two",
    )
    _create_agent(
        db_session,
        email="other.agent@example.com",
        name="Other Agent",
    )

    db_session.add(
        User(
            email="target.user@example.com",
            password_hash=PasswordCrypto.hash_password("any_password"),
            is_email_verified=True,
            role=UserRole.user,
        )
    )
    db_session.flush()

    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}?email=target.agent",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert all("target.agent" in item["email"] for item in data["items"])


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_filters_by_name(
    client,
    logged_in_user,
    db_session,
):
    _create_agent(
        db_session,
        email="name.target.1@example.com",
        name="Target Alpha",
    )
    _create_agent(
        db_session,
        email="name.target.2@example.com",
        name="beta target",
    )
    _create_agent(
        db_session,
        email="name.other@example.com",
        name="Not matching",
    )
    _create_agent(
        db_session,
        email="name.null@example.com",
        name=None,
    )

    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}?name=target",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert all("target" in item["name"].lower() for item in data["items"])


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_filters_by_phone_number(
    client,
    logged_in_user,
    db_session,
):
    _create_agent(
        db_session,
        email="phone.target.1@example.com",
        phone_number="+420701111111",
    )
    _create_agent(
        db_session,
        email="phone.target.2@example.com",
        phone_number="+420701111222",
    )
    _create_agent(
        db_session,
        email="phone.other@example.com",
        phone_number="+420702222222",
    )
    _create_agent(
        db_session,
        email="phone.null@example.com",
        phone_number=None,
    )

    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}?phone_number=701111",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert all("701111" in item["phone_number"] for item in data["items"])


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_returns_only_agents(
    client,
    logged_in_user,
    db_session,
):
    _create_agent(
        db_session,
        email="only.agent@example.com",
        name="Only Agent",
    )

    db_session.add_all(
        [
            User(
                email="not.agent.user@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                name="Only Agent",
            ),
            User(
                email="not.agent.admin@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.admin,
                name="Only Agent",
            ),
        ]
    )
    db_session.flush()

    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}?name=Only Agent",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == "only.agent@example.com"


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_counts_only_active_estates(
    client,
    logged_in_user,
    db_session,
):
    agent_with_two_active = _create_agent(
        db_session,
        email="estate.qty.2@example.com",
        name="Estate Qty Two",
    )
    agent_with_one_active = _create_agent(
        db_session,
        email="estate.qty.1@example.com",
        name="Estate Qty One",
    )
    agent_with_zero_active = _create_agent(
        db_session,
        email="estate.qty.0@example.com",
        name="Estate Qty Zero",
    )

    _create_estate_for_agent(
        db_session,
        agent_id=agent_with_two_active.id,
        status=ListingStatus.active,
    )
    _create_estate_for_agent(
        db_session,
        agent_id=agent_with_two_active.id,
        status=ListingStatus.active,
    )
    _create_estate_for_agent(
        db_session,
        agent_id=agent_with_two_active.id,
        status=ListingStatus.draft,
    )
    _create_estate_for_agent(
        db_session,
        agent_id=agent_with_one_active.id,
        status=ListingStatus.active,
    )
    _create_estate_for_agent(
        db_session,
        agent_id=agent_with_zero_active.id,
        status=ListingStatus.archived,
    )

    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}"
        "?email=estate.qty&sort_by=estate_qty&sort_order=desc",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    items = response.get_json()["data"]["items"]

    assert [item["email"] for item in items] == [
        "estate.qty.2@example.com",
        "estate.qty.1@example.com",
        "estate.qty.0@example.com",
    ]
    assert [item["estate_qty"] for item in items] == [2, 1, 0]


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_sorts_by_email_desc(
    client,
    logged_in_user,
    populate_agents,
):
    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}"
        "?sort_by=email&sort_order=desc&page_size=50",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    emails = [item["email"] for item in response.get_json()["data"]["items"]]
    assert emails == sorted(emails, reverse=True)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_agents_admin_sorts_by_created_at_desc(
    client,
    logged_in_user,
    db_session,
):
    base_dt = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)

    _create_agent(
        db_session,
        email="created-sort-1@example.com",
        created_at=base_dt,
    )
    _create_agent(
        db_session,
        email="created-sort-2@example.com",
        created_at=base_dt + datetime.timedelta(days=1),
    )
    _create_agent(
        db_session,
        email="created-sort-3@example.com",
        created_at=base_dt + datetime.timedelta(days=2),
    )

    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}"
        "?email=created-sort&sort_by=created_at&sort_order=desc",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    emails = [item["email"] for item in response.get_json()["data"]["items"]]
    assert emails == [
        "created-sort-3@example.com",
        "created-sort-2@example.com",
        "created-sort-1@example.com",
    ]


@pytest.mark.parametrize(
    "logged_in_user",
    [UserRole.user, UserRole.agent],
    indirect=True,
)
def test_list_agents_forbidden_for_non_admin(client, logged_in_user):
    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "forbidden"


def test_list_agents_unauthorized_without_token(client):
    response = client.get(f"{API_PREFIX}{ADMIN_AGENTS_PATH}")

    assert response.status_code == 401


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
@pytest.mark.parametrize(
    "query",
    [
        "page=0",
        "page_size=0",
        "page_size=999",
        "sort_by=invalid",
        "sort_order=sideways",
    ],
)
def test_list_agents_invalid_query_validation_error(
    client,
    logged_in_user,
    query,
):
    response = client.get(
        f"{API_PREFIX}{ADMIN_AGENTS_PATH}?{query}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "request_validation_error"
