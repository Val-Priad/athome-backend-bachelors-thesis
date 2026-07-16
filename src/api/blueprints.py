from flask import Flask

from api.admin.agents.admin_agents_router import bp as admin_agents_bp
from api.admin.estate.admin_estate_router import bp as admin_estate_bp
from api.admin.users.admin_users_router import bp as admin_users_bp
from api.agents.agents_router import bp as agent_bp
from api.auth.auth_router import bp as auth_bp
from api.estate.estate_router import bp as estate_bp
from api.users.me.me_router import bp as me_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(me_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(estate_bp)
    app.register_blueprint(admin_estate_bp)
    app.register_blueprint(admin_agents_bp)
