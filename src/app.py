from flask import Flask

from api.admin.agents.admin_agents_router import bp as admin_agents_bp
from api.admin.estate.admin_estate_router import bp as admin_estate_bp
from api.admin.users.admin_users_router import bp as admin_users_bp
from api.agents.agents_router import bp as agent_bp
from api.auth.auth_router import bp as auth_bp
from api.error_handlers import register_error_handler
from api.estate.estate_router import bp as estate_bp
from api.users.me.me_router import bp as me_bp
from config import FlaskConfig
from exceptions.error_catalog import register_errors
from infrastructure.db import init_db
from infrastructure.jwt.jwt_config import create_jwt_manager
from infrastructure.jwt.jwt_handlers import register_jwt_handlers
from infrastructure.logging.setup_logging import setup_logging
from infrastructure.rate_limiting.limiter_config import create_limiter


def create_app(config: type[FlaskConfig]) -> Flask:
    setup_logging()
    app = Flask(__name__)

    app.config.from_object(config)
    init_db(app)

    create_limiter(app)
    create_jwt_manager(app)

    register_jwt_handlers(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(me_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(estate_bp)
    app.register_blueprint(admin_estate_bp)
    app.register_blueprint(admin_agents_bp)

    register_errors()
    register_error_handler(app)

    return app
