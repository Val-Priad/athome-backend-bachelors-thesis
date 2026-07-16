from flask_jwt_extended import (
    JWTManager,
)

from infrastructure.jwt.jwt_error_handlers import (
    register_jwt_error_handlers,
)

jwt = JWTManager()
register_jwt_error_handlers(jwt)
