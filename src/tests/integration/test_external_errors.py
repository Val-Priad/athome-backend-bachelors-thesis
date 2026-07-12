from datetime import timedelta

import pytest
from flask_jwt_extended import (
    create_access_token,
    decode_token,
    jwt_required,
)

from infrastructure.jwt.jwt_config import jwt
from tests.integration.conftest import ADMIN_USERS_PATH, AUTH_PATH


def assert_error_response(
    response,
    *,
    status: int,
    code: str,
    message: str,
) -> None:
    assert response.status_code == status
    assert response.get_json() == {
        "error": {
            "code": code,
            "message": message,
        }
    }


def set_access_token_cookie(client, app, token: str) -> None:
    client.set_cookie(
        app.config["JWT_ACCESS_COOKIE_NAME"],
        token,
    )


@pytest.fixture
def restore_blocklist_callback():
    original_callback = jwt._token_in_blocklist_callback

    yield

    jwt._token_in_blocklist_callback = original_callback


def test_login_invalid_type_of_content(client):
    response = client.post(
        f"{AUTH_PATH}/login",
        data="email=user@example.com&password=45245",  # NOSONAR
        content_type="text/plain",
    )

    assert response.status_code == 415
    assert response.get_json()["error"]["code"] == "unsupported_media_type"


def test_get_user_by_id_not_logged_in(client, any_user):
    response = client.get(
        f"{ADMIN_USERS_PATH}/{any_user.id}",
    )

    assert_error_response(
        response,
        status=401,
        code="no_authorization",
        message="Authentication is required",
    )


def test_get_user_by_id_with_expired_token(client, app, any_user):
    with app.app_context():
        access_token = create_access_token(
            identity=str(any_user.id),
            expires_delta=timedelta(seconds=-1),
        )

    set_access_token_cookie(client, app, access_token)

    response = client.get(
        f"{ADMIN_USERS_PATH}/{any_user.id}",
    )

    assert_error_response(
        response,
        status=401,
        code="token_expired",
        message="Authentication token has expired",
    )


def test_get_user_by_id_with_invalid_token(client, app, any_user):
    set_access_token_cookie(
        client,
        app,
        "not-a-valid-jwt",
    )

    response = client.get(
        f"{ADMIN_USERS_PATH}/{any_user.id}",
    )

    assert_error_response(
        response,
        status=401,
        code="invalid_token",
        message="Authentication token is invalid",
    )


def test_get_user_by_id_with_revoked_token(
    client,
    app,
    any_user,
    restore_blocklist_callback,
):
    with app.app_context():
        access_token = create_access_token(
            identity=str(any_user.id),
        )
        revoked_jti = decode_token(access_token)["jti"]

    @jwt.token_in_blocklist_loader
    def is_token_revoked(_jwt_header: dict, jwt_payload: dict) -> bool:
        return jwt_payload["jti"] == revoked_jti

    set_access_token_cookie(client, app, access_token)

    response = client.get(
        f"{ADMIN_USERS_PATH}/{any_user.id}",
    )

    assert_error_response(
        response,
        status=401,
        code="token_revoked",
        message="Authentication token has been revoked",
    )


def test_non_fresh_token_is_rejected_by_fresh_endpoint(
    client,
    app,
    any_user,
):
    endpoint = "/test/fresh-token-required"

    @jwt_required(fresh=True)
    def fresh_token_required():
        return {"message": "OK"}

    app.add_url_rule(
        endpoint,
        endpoint="test_fresh_token_required",
        view_func=fresh_token_required,
        methods=["GET"],
    )

    with app.app_context():
        access_token = create_access_token(
            identity=str(any_user.id),
            fresh=False,
        )

    set_access_token_cookie(client, app, access_token)

    response = client.get(endpoint)

    assert_error_response(
        response,
        status=401,
        code="fresh_token_required",
        message="Fresh authentication is required",
    )


def test_unexpected_exception_returns_generic_500(client, app):
    endpoint = "/test/unexpected-error"

    def raise_unexpected_error():
        raise RuntimeError("Sensitive internal information")

    app.add_url_rule(
        endpoint,
        endpoint="test_unexpected_error",
        view_func=raise_unexpected_error,
        methods=["GET"],
    )

    response = client.get(endpoint)

    assert_error_response(
        response,
        status=500,
        code="internal_server_error",
        message="Internal server error",
    )
