from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_error, construct_response
from composition_root import get_admin_filtered_estate_use_case
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.estate_schemas.requests.estate_filter_request import (
    EstateAdminFilterRequest,
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


# TODO: update_estate # NOSONAR


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)
