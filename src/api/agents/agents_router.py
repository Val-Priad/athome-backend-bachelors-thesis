from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_error, construct_response
from composition_root import (
    get_agent_description_use_case,
    get_agent_own_estates_use_case,
)
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.estate_schemas.requests.estate_filter_request import (
    EstateAgentOwnFilterRequest,
)
from schemas.helpers import parse_query_params

bp = Blueprint("agent", __name__, url_prefix="/api/agents")


@bp.get("/<uuid:agent_id>")
def get_agent_description(agent_id: UUID):
    agent_description = get_agent_description_use_case.execute(agent_id)
    return construct_response(data=agent_description)


@bp.get("/me/estate")
@jwt_required()
def get_my_estates():
    requester_id = get_jwt_user_uuid()

    raw_filters = parse_query_params(
        schema_cls=EstateAgentOwnFilterRequest,
        args=request.args,
    )
    filters = EstateAgentOwnFilterRequest.from_request(raw_filters)

    response = get_agent_own_estates_use_case.execute(
        requester_id=requester_id,
        filters=filters,
    )

    return construct_response(data=response)


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)
