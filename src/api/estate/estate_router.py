from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_error, construct_response
from composition_root import create_estate_use_case, suggest_estate_use_case
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.estate_schemas.estate_create_request import EstateCreateRequest
from schemas.estate_schemas.estate_suggest_request import EstateSuggestRequest

bp = Blueprint("estate", __name__, url_prefix="/api/estate")


# @bp.get("/<uuid:estate_id>")
# def get_estate_description(estate_id: UUID):
#     estate_description = .execute(estate_id)
#     return construct_response(data=estate_description)


@bp.post("")
@jwt_required()
def create_estate():
    requester_id = get_jwt_user_uuid()
    data = EstateCreateRequest.from_request(request.json)
    response = create_estate_use_case.execute(data, requester_id)
    return construct_response(status=201, data=response)


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
