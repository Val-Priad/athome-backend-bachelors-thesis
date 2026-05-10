from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.v1.responses import construct_error, construct_response
from composition_root import (
    delete_me_use_case,
    get_me_use_case,
    update_password_use_case,
    update_personal_data_use_case,
)
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.me_schemas.me_requests import (
    PasswordRequest,
    UpdateUserPersonalDataRequest,
)

bp = Blueprint("users_me", __name__, url_prefix="/api/v1/users/me")


# TODO: All logic must be in service, no orchestration in router
@bp.get("/")
@jwt_required()
def get_me():
    user_id = get_jwt_user_uuid()

    user_response = get_me_use_case.execute(user_id)
    return construct_response(data=user_response)


@bp.delete("/")
@jwt_required()
def delete_me():
    user_id = get_jwt_user_uuid()

    delete_me_use_case.execute(user_id)
    return construct_response()


@bp.patch("/update_password")
@jwt_required()
def update_password():
    data = PasswordRequest.from_request(request.json)

    user_id = get_jwt_user_uuid()
    update_password_use_case.execute(
        user_id, data.old_password, data.new_password
    )
    return construct_response()


@bp.patch("/update-personal-data")
@jwt_required()
def update_personal_data():
    data = UpdateUserPersonalDataRequest.from_request(request.json)

    user_id = get_jwt_user_uuid()
    user_response = update_personal_data_use_case.execute(user_id, data)
    return construct_response(
        data=user_response,
        message="User personal data was updated successfully",
    )


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)
