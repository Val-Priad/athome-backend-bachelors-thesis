from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_response
from composition_root import (
    email_to_agent_use_case,
    get_estate_use_case,
    get_filtered_estate_use_case,
    suggest_estate_use_case,
    toggle_saved_estate_use_case,
)
from infrastructure.jwt.jwt_utils import (
    get_jwt_user_uuid,
    get_optional_jwt_user_uuid,
)
from infrastructure.rate_limiting.limiter_config import limiter
from schemas.estate_schemas.requests.email_to_agent_request import (
    EmailToAgentRequest,
)
from schemas.estate_schemas.requests.estate_filter_request import (
    EstatePublicFilterRequest,
)
from schemas.estate_schemas.requests.estate_suggest_request import (
    EstateSuggestRequest,
)
from schemas.helpers import parse_query_params

bp = Blueprint("estate", __name__, url_prefix="/api/estate")


@bp.get("/<uuid:estate_id>")
@jwt_required(optional=True)
def get_estate(estate_id: UUID):
    requester_id = get_optional_jwt_user_uuid()
    response = get_estate_use_case.execute(requester_id, estate_id)
    return construct_response(data=response)


@bp.get("")
@jwt_required(optional=True)
def get_estates():
    requester_id = get_optional_jwt_user_uuid()
    raw_filters = parse_query_params(
        schema_cls=EstatePublicFilterRequest,
        args=request.args,
    )
    filters = EstatePublicFilterRequest.from_request(raw_filters)
    response = get_filtered_estate_use_case.execute(filters, requester_id)
    return construct_response(data=response)


@bp.post("/suggestions")
@jwt_required()
def suggest_estate():
    requester_id = get_jwt_user_uuid()
    data = EstateSuggestRequest.from_request(request.json)
    response = suggest_estate_use_case.execute(data, requester_id)
    return construct_response(status=201, data=response)


@bp.post("/saved/<uuid:estate_id>")
@jwt_required()
def toggle_saved_estate(estate_id):
    requester_id = get_jwt_user_uuid()
    toggle_saved_estate_use_case.execute(requester_id, estate_id)
    return construct_response()


@bp.post("/<uuid:estate_id>/contact")
@limiter.limit("3/minute")
def send_email_to_estate_agent(estate_id):
    payload = EmailToAgentRequest.from_request(request.json)
    email_to_agent_use_case.execute(estate_id, payload)
    return construct_response()
