from flask import Blueprint
from flask_jwt_extended import jwt_required

testing_bp = Blueprint(
    "integration_testing",
    __name__,
    url_prefix="/test",
)


@testing_bp.get("/fresh-token-required")
@jwt_required(fresh=True)
def fresh_token_required():
    return {"message": "OK"}


@testing_bp.get("/unexpected-error")
def unexpected_error():
    raise RuntimeError("Sensitive internal information")
