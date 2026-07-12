from flask import Response
from flask_jwt_extended import JWTManager, unset_jwt_cookies

from api.responses import construct_error


def register_jwt_error_handlers(jwt: JWTManager) -> None:
    @jwt.unauthorized_loader
    def handle_missing_token(reason: str) -> Response:
        return construct_error(code="no_authorization")

    @jwt.expired_token_loader
    def handle_expired_token(
        jwt_header: dict,
        jwt_payload: dict,
    ) -> Response:
        response = construct_error(code="token_expired")
        unset_jwt_cookies(response)
        return response

    @jwt.invalid_token_loader
    def handle_invalid_token(reason: str) -> Response:
        response = construct_error(code="invalid_token")
        unset_jwt_cookies(response)
        return response

    @jwt.revoked_token_loader
    def handle_revoked_token(
        jwt_header: dict,
        jwt_payload: dict,
    ) -> Response:
        response = construct_error(code="token_revoked")
        unset_jwt_cookies(response)
        return response

    @jwt.needs_fresh_token_loader
    def handle_non_fresh_token(
        jwt_header: dict,
        jwt_payload: dict,
    ) -> Response:
        return construct_error(code="fresh_token_required")
