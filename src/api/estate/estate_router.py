from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_error, construct_response
from composition_root import post_draft_estate_use_case
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.estate_schemas.draft_request import EstateDraftRequest

bp = Blueprint("estate", __name__, url_prefix="/api/estate")


# @bp.get("/<uuid:estate_id>")
# def get_estate_description(estate_id: UUID):
#     estate_description = .execute(estate_id)
#     return construct_response(data=estate_description)


@bp.post("")
@jwt_required()
def post_draft_estate():
    requester_id = get_jwt_user_uuid()
    data = EstateDraftRequest.from_request(request.json)
    post_draft_estate_use_case.execute(data, requester_id)
    return construct_response()


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)
