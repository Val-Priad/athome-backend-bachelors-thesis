from uuid import UUID

from flask import Blueprint

from api.responses import construct_error, construct_response
from composition_root import get_agent_description_use_case

bp = Blueprint("agent", __name__, url_prefix="/api/agent")


@bp.get("/<uuid:agent_id>")
def get_agent_description(agent_id: UUID):
    agent_description = get_agent_description_use_case.execute(agent_id)
    return construct_response(data=agent_description)


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    return construct_error(e)
