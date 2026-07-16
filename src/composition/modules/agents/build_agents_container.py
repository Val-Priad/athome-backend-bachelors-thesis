from application.agent.get_agent_description_use_case import (
    GetAgentDescriptionUseCase,
)
from application.estate.estate_response_mapper import EstateResponseMapper
from application.estate.get_agent_own_estates_use_case import (
    GetAgentOwnEstatesUseCase,
)
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from composition.modules.agents.agents_container import AgentsContainer
from composition.services.service_container import ServiceContainer


def build_agents_container(
    infrastructure: InfrastructureContainer,
    services: ServiceContainer,
    estate_response_mapper: EstateResponseMapper,
) -> AgentsContainer:
    transactions = infrastructure.transactions

    return AgentsContainer(
        get_description=GetAgentDescriptionUseCase(
            transactions=transactions,
            agent_service=services.agents,
        ),
        get_own_estates=GetAgentOwnEstatesUseCase(
            transactions=transactions,
            estate_service=services.estates,
            authorization_service=services.authorization,
            response_mapper=estate_response_mapper,
        ),
    )
