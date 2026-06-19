from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_error, construct_response
from composition_root import (
    create_estate_use_case,
    get_estate_use_case,
    get_filtered_estate_use_case,
    suggest_estate_use_case,
)
from infrastructure.jwt.jwt_utils import (
    get_jwt_user_uuid,
    get_optional_jwt_user_uuid,
)
from schemas.estate_schemas.requests.estate_create_request import (
    EstateCreateRequest,
)
from schemas.estate_schemas.requests.estate_filter_request import (
    EstatePublicFilterRequest,
)
from schemas.estate_schemas.requests.estate_suggest_request import (
    EstateSuggestRequest,
)
from schemas.helpers import parse_query_params

bp = Blueprint("estate", __name__, url_prefix="/api/estate")


# @bp.get("/<uuid:estate_id>")
# def get_estate_description(estate_id: UUID):
#     estate_description = .execute(estate_id)
#     return construct_response(data=estate_description)

# TODO: list estate # NOSONAR
# TODO: save estate to liked # NOSONAR


@bp.get("/<uuid:estate_id>")
@jwt_required(optional=True)
def get_estate(estate_id: UUID):
    requester_id = get_optional_jwt_user_uuid()
    response = get_estate_use_case.execute(requester_id, estate_id)
    return construct_response(data=response)


@bp.post("/")
@jwt_required()
def create_estate():
    # TODO: think about combining suggest route and create route # NOSONAR
    requester_id = get_jwt_user_uuid()
    data = EstateCreateRequest.from_request(request.json)
    response = create_estate_use_case.execute(data, requester_id)
    return construct_response(status=201, data=response)


@bp.get("/")
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


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)
