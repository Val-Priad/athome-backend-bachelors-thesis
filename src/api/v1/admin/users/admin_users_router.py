from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.v1.responses import construct_error, construct_response
from composition_root import (
    change_user_role_use_case,
    delete_admin_user_use_case,
    get_admin_user_use_case,
)
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.admin_schemas.admin_users_schemas.admin_users_requests import (
    RoleRequest,
)

bp = Blueprint("admin_users", __name__, url_prefix="/api/v1/admin/users")


@bp.get("/<uuid:user_id>")
@jwt_required()
def get_user(user_id: UUID):
    requester_id = get_jwt_user_uuid()
    user_response = get_admin_user_use_case.execute(requester_id, user_id)
    return construct_response(data=user_response)


@bp.patch("/<uuid:user_id>/role")
@jwt_required()
def change_user_role(user_id: UUID):
    requester_id = get_jwt_user_uuid()

    data = RoleRequest.from_request(request.json)

    change_user_role_use_case.execute(requester_id, user_id, data.role)
    return construct_response()


@bp.delete("/<uuid:user_id>")
@jwt_required()
def delete_user(user_id: UUID):
    requester_id = get_jwt_user_uuid()

    delete_admin_user_use_case.execute(requester_id, user_id)
    return construct_response()


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)


# TODO: Read users list (GDPR safe fields only)
# TODO: Add filters for users list
# TODO: Add sorting for users list
