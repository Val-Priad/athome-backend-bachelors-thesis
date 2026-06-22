import datetime

import pytest

from domain.user.user_model import User, UserRole
from schemas.admin_schemas.admin_users_schemas.admin_users_responses import (
    UsersListItem,
)
from security.password_crypto import PasswordCrypto
from tests.integration.conftest import ADMIN_USERS_PATH, API_PREFIX


@pytest.fixture
def populate_users(db_session):
    for i in range(37):
        db_session.add(
            User(
                email=f"user_{i}@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
            )
        )

    for i in range(9):
        db_session.add(
            User(
                email=f"agent_{i}@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.agent,
            )
        )

    for i in range(4):
        db_session.add(
            User(
                email=f"admin_{i}@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.admin,
            )
        )
    db_session.flush()


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_success_defaults(
    client, logged_in_user, populate_users
):
    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    body = response.get_json()
    data = body["data"]

    assert data["total"] == 51
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) == 20

    first_item = data["items"][0]
    UsersListItem.model_validate(first_item)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_supports_pagination(
    client, logged_in_user, populate_users
):
    response_page_1 = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?page=1&page_size=15&sort_by=email&sort_order=asc",
        headers=logged_in_user.headers,
    )

    response_page_2 = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?page=2&page_size=15&sort_by=email&sort_order=asc",
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
    assert data["total"] == 51
    assert data["page"] == 2
    assert data["page_size"] == 15
    assert len(data["items"]) == 15

    emails = [item["email"] for item in data["items"]]
    assert emails == sorted(emails)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_filters_by_role(client, logged_in_user, db_session):
    db_session.add_all(
        [
            User(
                email="role.user@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
            ),
            User(
                email="role.agent@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.agent,
            ),
            User(
                email="role.admin@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.admin,
            ),
        ]
    )
    db_session.flush()

    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?role=agent",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["total"] == 1
    assert len(data["items"]) == 1

    item = data["items"][0]
    assert item["email"] == "role.agent@example.com"
    assert item["role"] == "agent"


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_filters_by_email(client, logged_in_user, db_session):
    db_session.add_all(
        [
            User(
                email="target.1@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
            ),
            User(
                email="target.2@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=False,
                role=UserRole.agent,
            ),
            User(
                email="other@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
            ),
        ]
    )
    db_session.flush()

    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?email=target",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    data = response.get_json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert all("target" in item["email"] for item in data["items"])


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_filters_by_name(client, logged_in_user, db_session):
    db_session.add_all(
        [
            User(
                email="name.target.1@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                name="Target Alpha",
            ),
            User(
                email="name.target.2@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.agent,
                name="beta target",
            ),
            User(
                email="name.other@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                name="Not matching",
            ),
            User(
                email="name.null@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                name=None,
            ),
        ]
    )
    db_session.flush()

    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?name=target",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    data = response.get_json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert all("target" in item["name"].lower() for item in data["items"])


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_filters_by_phone_number(
    client, logged_in_user, db_session
):
    db_session.add_all(
        [
            User(
                email="phone.target.1@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                phone_number="+14155552671",
            ),
            User(
                email="phone.target.2@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=False,
                role=UserRole.agent,
                phone_number="+14155552672",
            ),
            User(
                email="phone.other@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                phone_number="+14156660000",
            ),
            User(
                email="phone.null@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                phone_number=None,
            ),
        ]
    )
    db_session.flush()

    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?phone_number=5555267",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    data = response.get_json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert all("5555267" in item["phone_number"] for item in data["items"])


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_filters_by_is_email_verified(
    client, logged_in_user, db_session
):
    db_session.add_all(
        [
            User(
                email="verified_true@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
            ),
            User(
                email="verified_false@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=False,
                role=UserRole.user,
            ),
        ]
    )
    db_session.flush()

    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?is_email_verified=false",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    data = response.get_json()["data"]
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == "verified_false@example.com"
    assert data["items"][0]["is_email_verified"] is False


@pytest.mark.parametrize(
    "logged_in_user", [UserRole.user, UserRole.agent], indirect=True
)
def test_list_users_forbidden_for_non_admin(client, logged_in_user):
    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "forbidden"


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_sorts_by_email_desc(
    client, logged_in_user, populate_users
):
    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?sort_by=email&sort_order=desc&page_size=50",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    emails = [item["email"] for item in response.get_json()["data"]["items"]]
    assert emails == sorted(emails, reverse=True)


@pytest.mark.parametrize("logged_in_user", [UserRole.admin], indirect=True)
def test_list_users_admin_sorts_by_created_at_desc(
    client, logged_in_user, db_session
):
    base_dt = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)

    db_session.add_all(
        [
            User(
                email="created-sort-1@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                created_at=base_dt,
            ),
            User(
                email="created-sort-2@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                created_at=base_dt + datetime.timedelta(days=1),
            ),
            User(
                email="created-sort-3@example.com",
                password_hash=PasswordCrypto.hash_password("any_password"),
                is_email_verified=True,
                role=UserRole.user,
                created_at=base_dt + datetime.timedelta(days=2),
            ),
        ]
    )
    db_session.flush()

    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?email=created-sort&sort_by=created_at&sort_order=desc&page_size=10",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 200

    emails = [item["email"] for item in response.get_json()["data"]["items"]]
    assert emails == [
        "created-sort-3@example.com",
        "created-sort-2@example.com",
        "created-sort-1@example.com",
    ]


def test_list_users_unauthorized_without_token(client):
    response = client.get(f"{API_PREFIX}{ADMIN_USERS_PATH}")
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
        "is_email_verified=maybe",
    ],
)
def test_list_users_invalid_query_validation_error(
    client, logged_in_user, query
):
    response = client.get(
        f"{API_PREFIX}{ADMIN_USERS_PATH}?{query}",
        headers=logged_in_user.headers,
    )
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "request_validation_error"
