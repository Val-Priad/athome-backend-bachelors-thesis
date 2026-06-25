from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_error, construct_response
from composition_root import (
    create_estate_use_case,
    delete_estate_use_case,
    get_admin_filtered_estate_use_case,
    update_estate_use_case,
)
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.estate_schemas.requests.estate_create_request import (
    EstateCreateRequest,
)
from schemas.estate_schemas.requests.estate_filter_request import (
    EstateAdminFilterRequest,
)
from schemas.estate_schemas.requests.estate_update_request import (
    EstateUpdateRequest,
)
from schemas.helpers import parse_query_params

bp = Blueprint("admin_estate", __name__, url_prefix="/api/admin/estate")


@bp.get("")
@jwt_required()
def get_estates():
    requester_id = get_jwt_user_uuid()
    raw_filters = parse_query_params(
        schema_cls=EstateAdminFilterRequest,
        args=request.args,
    )
    filters = EstateAdminFilterRequest.from_request(raw_filters)
    response = get_admin_filtered_estate_use_case.execute(
        filters, requester_id
    )
    return construct_response(data=response)


@bp.post("")
@jwt_required()
def create_estate():
    requester_id = get_jwt_user_uuid()
    data = EstateCreateRequest.from_request(request.json)
    response = create_estate_use_case.execute(data, requester_id)
    return construct_response(status=201, data=response)


@bp.put("/<uuid:estate_id>")
@jwt_required()
def update_estate(estate_id: UUID):
    requester_id = get_jwt_user_uuid()
    data = EstateUpdateRequest.from_request(request.json)
    response = update_estate_use_case.execute(
        estate_id,
        data,
        requester_id,
    )
    return construct_response(data=response)


@bp.delete("/<uuid:estate_id>")
@jwt_required()
def delete_estate(estate_id: UUID):
    requester_id = get_jwt_user_uuid()
    delete_estate_use_case.execute(
        estate_id,
        requester_id,
    )
    return construct_response()


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)
