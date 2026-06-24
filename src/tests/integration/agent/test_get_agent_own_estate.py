import uuid

import pytest

from domain.estate.enums.estate_listing_enums import ListingStatus
from domain.user.user_model import UserRole
from tests.integration.conftest import AGENTS_PATH
from tests.integration.estate.test_filter_estate import (
    assert_ok_filter_response,
    create_filter_estate,
)

AGENT_OWN_ESTATE_PATH = f"{AGENTS_PATH}/me/estate"


def _get_response_ids(response) -> set[str]:
    body = response.get_json()
    return {item["id"] for item in body["data"]["items"]}


def test_get_agent_own_estates_unauthorized_without_token(client):
    response = client.get(AGENT_OWN_ESTATE_PATH)

    assert response.status_code == 401


@pytest.mark.parametrize(
    "logged_in_user",
    [UserRole.user, UserRole.admin],
    indirect=True,
)
def test_get_agent_own_estates_forbidden_for_non_agent(
    client,
    logged_in_user,
):
    response = client.get(
        AGENT_OWN_ESTATE_PATH,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 403


@pytest.mark.parametrize("logged_in_user", [UserRole.agent], indirect=True)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_get_agent_own_estates_returns_only_current_agent_estates(
    client,
    db_session,
    logged_in_user,
    any_user,
):
    own_active_id = create_filter_estate(
        db_session,
        title="Current agent active estate",
        status=ListingStatus.active,
        agent_id=logged_in_user.id,
    )
    own_draft_id = create_filter_estate(
        db_session,
        title="Current agent draft estate",
        status=ListingStatus.draft,
        agent_id=logged_in_user.id,
    )
    other_agent_estate_id = create_filter_estate(
        db_session,
        title="Other agent estate",
        status=ListingStatus.active,
        agent_id=any_user.id,
    )

    response = client.get(
        AGENT_OWN_ESTATE_PATH,
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=2)
    response_ids = _get_response_ids(response)

    assert response_ids == {str(own_active_id), str(own_draft_id)}
    assert str(other_agent_estate_id) not in response_ids
    assert len(data["items"]) == 2


@pytest.mark.parametrize("logged_in_user", [UserRole.agent], indirect=True)
@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_get_agent_own_estates_ignores_external_agent_identity(
    client,
    db_session,
    logged_in_user,
    any_user,
):
    own_estate_id = create_filter_estate(
        db_session,
        title="Current agent estate",
        status=ListingStatus.active,
        agent_id=logged_in_user.id,
    )
    other_agent_estate_id = create_filter_estate(
        db_session,
        title="Other agent estate",
        status=ListingStatus.active,
        agent_id=any_user.id,
    )

    response = client.get(
        AGENT_OWN_ESTATE_PATH,
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=1)
    response_ids = _get_response_ids(response)

    assert response_ids == {str(own_estate_id)}
    assert str(other_agent_estate_id) not in response_ids
    assert len(data["items"]) == 1


@pytest.mark.parametrize("logged_in_user", [UserRole.agent], indirect=True)
def test_get_agent_own_estates_can_return_not_active_estates(
    client,
    db_session,
    logged_in_user,
):
    draft_id = create_filter_estate(
        db_session,
        title="Agent draft estate",
        status=ListingStatus.draft,
        agent_id=logged_in_user.id,
    )

    response = client.get(
        AGENT_OWN_ESTATE_PATH,
        headers=logged_in_user.headers,
    )

    data = assert_ok_filter_response(response, total=1)

    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(draft_id)


@pytest.mark.parametrize("logged_in_user", [UserRole.agent], indirect=True)
@pytest.mark.parametrize(
    ("query_string", "field_name"),
    [
        ({"agent_id": str(uuid.uuid4())}, "agent_id"),
        ({"seller_id": str(uuid.uuid4())}, "seller_id"),
        ({"saved_by_current_user": "true"}, "saved_by_current_user"),
    ],
)
def test_get_agent_own_estates_rejects_forbidden_query_params(
    client,
    logged_in_user,
    query_string,
    field_name,
):
    response = client.get(
        AGENT_OWN_ESTATE_PATH,
        query_string=query_string,
        headers=logged_in_user.headers,
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["error"]["code"] == "request_validation_error"
    assert any(
        error["field"].endswith(field_name)
        for error in body["error"].get("errors", [])
    )
