from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_response
from composition.container_access import get_application_container
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.estate_schemas.requests.estate_filter_request import (
    EstateAgentOwnFilterRequest,
)
from schemas.helpers import parse_query_params

bp = Blueprint("agent", __name__, url_prefix="/api/agents")


@bp.get("/<uuid:agent_id>")
def get_agent_description(agent_id: UUID):
    container = get_application_container()
    agent_description = container.agents.get_description.execute(agent_id)
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

    container = get_application_container()
    response = container.agents.get_own_estates.execute(
        requester_id=requester_id,
        filters=filters,
    )

    return construct_response(data=response)
