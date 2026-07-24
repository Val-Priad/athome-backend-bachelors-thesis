from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.responses import construct_response
from composition.container_access import get_application_container
from infrastructure.jwt.jwt_utils import get_jwt_user_uuid
from schemas.media_schemas.requests.media_upload_url_request import (
    MediaUploadUrlRequest,
)

bp = Blueprint("media", __name__, url_prefix="/api/media")


@bp.post("/upload-url")
@jwt_required()
def create_upload_url():
    requester_id = get_jwt_user_uuid()
    data = MediaUploadUrlRequest.from_request(request.json)
    container = get_application_container()
    response = container.media.create_upload_url.execute(data, requester_id)
    return construct_response(data=response)
