from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_error, construct_response
from composition_root import list_agents_use_case
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.admin_schemas.admin_users_schemas.admin_agents_request import (
    AgentListRequest,
)

bp = Blueprint("admin_agents", __name__, url_prefix="/api/admin/agents")


@bp.get("")
@jwt_required()
def list_users():
    requester_id = get_jwt_user_uuid()
    query = AgentListRequest.from_query(request.args)

    response = list_agents_use_case.execute(requester_id, query)
    return construct_response(data=response)


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)


# TODO: agent estate management view # NOSONAR
