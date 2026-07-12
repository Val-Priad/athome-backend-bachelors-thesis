from flask import Flask
from flask_jwt_extended import (
    JWTManager,
)

from infrastructure.jwt.jwt_error_handlers import (
    register_jwt_error_handlers,
)

jwt = JWTManager()


def create_jwt_manager(app: Flask) -> None:
    jwt.init_app(app)
    register_jwt_error_handlers(jwt)
