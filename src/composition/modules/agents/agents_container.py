from dataclasses import dataclass

from application.agent.get_agent_description_use_case import (
    GetAgentDescriptionUseCase,
)
from application.estate.get_agent_own_estates_use_case import (
    GetAgentOwnEstatesUseCase,
)


@dataclass(frozen=True, slots=True)
class AgentsContainer:
    get_description: GetAgentDescriptionUseCase
    get_own_estates: GetAgentOwnEstatesUseCase
