from uuid import uuid4

import pytest

from domain.user.user_model import UserRole
from schemas.agent_schemas.agent_responses import AgentDescriptionResponse
from tests.integration.conftest import AGENTS_PATH


@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
@pytest.mark.parametrize(
    "logged_in_user",
    [UserRole.agent, UserRole.user, UserRole.admin],
    indirect=True,
)
def test_get_agent_description_successful(
    client, logged_in_user, any_user, db_session
):
    any_user.avatar_key = f"user-avatars/{any_user.id}/{uuid4()}.webp"
    db_session.flush()
    response = client.get(
        f"{AGENTS_PATH}/{any_user.id}",
        headers=logged_in_user.headers,
    )
    agent_dto: AgentDescriptionResponse = AgentDescriptionResponse.from_model(
        any_user
    )
    agent_json = agent_dto.model_dump(mode="json")
    agent_json["avatar_url"] = f"https://media.test/{any_user.avatar_key}"

    assert response.status_code == 200
    assert response.get_json()["data"] == agent_json


@pytest.mark.parametrize("any_user", [UserRole.agent], indirect=True)
def test_get_agent_description_successful_and_public(client, any_user):
    response = client.get(
        f"{AGENTS_PATH}/{any_user.id}",
    )
    agent_dto: AgentDescriptionResponse = AgentDescriptionResponse.from_model(
        any_user
    )
    agent_json = agent_dto.model_dump(mode="json")

    assert response.status_code == 200
    assert response.get_json()["data"] == agent_json


@pytest.mark.parametrize(
    "any_user", [UserRole.admin, UserRole.user], indirect=True
)
@pytest.mark.parametrize(
    "logged_in_user",
    [UserRole.agent],
    indirect=True,
)
def test_get_agent_description_fails_for_users_and_admins(
    client, logged_in_user, any_user
):
    response = client.get(
        f"{AGENTS_PATH}/{any_user.id}",
        headers=logged_in_user.headers,
    )

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "agent_not_found"


def test_get_agent_description_fails_for_user_who_not_exist(client):
    response = client.get(
        f"{AGENTS_PATH}/{uuid4()}",
    )

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "agent_not_found"
