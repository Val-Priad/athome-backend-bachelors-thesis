from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from api.responses import construct_error, construct_response
from composition.container_access import get_application_container
from exceptions.custom_exceptions.mailer_exceptions import EmailSendError
from exceptions.custom_exceptions.user_exceptions import (
    InvalidCredentialsError,
    PasswordVerificationError,
    UserAlreadyExistsError,
    UserAlreadyVerifiedError,
    UserIsNotVerifiedError,
    UserNotFoundError,
)
from infrastructure.rate_limiting.limiter_config import limiter
from schemas.auth_schemas.auth_requests import (
    EmailPasswordRequest,
    EmailRequest,
    TokenPasswordRequest,
    TokenRequest,
)

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
@limiter.limit("2/minute")
def register():
    data = EmailPasswordRequest.from_request(request.json)
    container = get_application_container()

    try:
        container.auth.register_user.execute(data)
    except (UserAlreadyExistsError, EmailSendError):
        pass
    return construct_response(
        message="If there was no user, it was created, following instructions were sent to an email",
        status=202,
    )


@bp.get("/verify-email")
def verify_token():
    data = TokenRequest.from_query(request.args)

    container = get_application_container()
    container.auth.verify_email.execute(data.token)
    return construct_response()


@bp.post("/resend-verification-email")
@limiter.limit("2/minute")
def resend_verification():
    data = EmailRequest.from_request(request.json)
    container = get_application_container()

    try:
        container.auth.resend_verification.execute(data.email)
    except (UserNotFoundError, UserAlreadyVerifiedError, EmailSendError):
        pass

    return construct_response(
        message="If the user exists and is not verified, a verification email has been sent",
        status=202,
    )


@bp.post("/login")
def login():
    data = EmailPasswordRequest.from_request(request.json)
    container = get_application_container()

    try:
        user_id = container.auth.login_user.execute(data.email, data.password)
    except (
        UserNotFoundError,
        UserIsNotVerifiedError,
        PasswordVerificationError,
    ):
        return construct_error(InvalidCredentialsError())
    access_token = create_access_token(identity=str(user_id), fresh=True)
    response = construct_response()
    set_access_cookies(response, access_token)
    return response


@bp.post("/logout")
@jwt_required()
def logout():
    response = construct_response()
    unset_jwt_cookies(response)
    return response


@bp.post("/reset-password")
@limiter.limit("2/minute")
def reset_password():
    data = EmailRequest.from_request(request.json)
    container = get_application_container()

    try:
        container.auth.reset_password.execute(data.email)
    except (UserNotFoundError, EmailSendError):
        pass

    return construct_response(
        message="If user exists, password reset has been sent", status=202
    )


@bp.post("/verify-new-password")
def verify_new_password():
    data = TokenPasswordRequest.from_request(request.json)

    container = get_application_container()
    container.auth.verify_new_password.execute(data.token, data.password)
    return construct_response()
