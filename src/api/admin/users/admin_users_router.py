from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_response
from composition.container_access import get_application_container
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.admin_schemas.admin_users_schemas.admin_users_requests import (
    RoleRequest,
    UsersListRequest,
)

bp = Blueprint("admin_users", __name__, url_prefix="/api/admin/users")


@bp.get("/<uuid:user_id>")
@jwt_required()
def get_user(user_id: UUID):
    requester_id = get_jwt_user_uuid()
    container = get_application_container()
    user_response = container.admin.get_user.execute(requester_id, user_id)
    return construct_response(data=user_response)


@bp.patch("/<uuid:user_id>/role")
@jwt_required()
def change_user_role(user_id: UUID):
    requester_id = get_jwt_user_uuid()

    data = RoleRequest.from_request(request.json)

    container = get_application_container()
    container.admin.change_user_role.execute(requester_id, user_id, data.role)
    return construct_response()


@bp.delete("/<uuid:user_id>")
@jwt_required()
def delete_user(user_id: UUID):
    requester_id = get_jwt_user_uuid()

    container = get_application_container()
    container.admin.delete_user.execute(requester_id, user_id)
    return construct_response()


@bp.get("")
@jwt_required()
def list_users():
    requester_id = get_jwt_user_uuid()
    query = UsersListRequest.from_query(request.args)

    container = get_application_container()
    response = container.admin.list_users.execute(requester_id, query)
    return construct_response(data=response)
