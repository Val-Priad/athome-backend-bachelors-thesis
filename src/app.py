from collections.abc import Mapping

from flask import Flask

from api.blueprints import register_blueprints
from api.error_handlers import register_error_handler
from composition.build_application_container import build_application_container
from composition.container_access import APPLICATION_CONTAINER_KEY
from composition.dependency_overrides import DependencyOverrides
from config import FlaskConfig
from configuration import configure_app
from exceptions.error_catalog import register_errors
from infrastructure.db import db
from infrastructure.jwt.jwt_config import jwt
from infrastructure.jwt.jwt_error_handlers import register_jwt_error_handlers
from infrastructure.jwt.jwt_handlers import register_jwt_handlers
from infrastructure.logging.setup_logging import setup_logging
from infrastructure.rate_limiting.limiter_config import limiter


def create_app(
    config: type[FlaskConfig],
    *,
    config_overrides: Mapping[str, object] | None = None,
    dependency_overrides: DependencyOverrides | None = None,
) -> Flask:
    app = Flask(__name__)

    configure_app(app, config, config_overrides)
    setup_logging(app)

    db.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    app.extensions[APPLICATION_CONTAINER_KEY] = build_application_container(
        app,
        overrides=dependency_overrides,
    )

    register_jwt_error_handlers(jwt)
    register_jwt_handlers(app)
    register_errors()
    register_error_handler(app)
    register_blueprints(app)

    return app
