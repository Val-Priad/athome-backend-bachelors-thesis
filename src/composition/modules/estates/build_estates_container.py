from application.estate.create_estate_use_case import CreateEstateUseCase
from application.estate.delete_estate_use_case import DeleteEstateUseCase
from application.estate.email_to_estate_agent_use_case import (
    EmailToAgentUseCase,
)
from application.estate.get_estate_use_case import GetEstateUseCase
from application.estate.get_filtered_estate_use_case import (
    GetFilteredEstateUseCase,
)
from application.estate.suggest_estate_use_case import SuggestEstateUseCase
from application.estate.toggle_saved_estate_use_case import (
    ToggleSavedEstateUseCase,
)
from application.estate.update_estate_use_case import UpdateEstateUseCase
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from composition.modules.estates.estates_container import EstatesContainer
from composition.repositories.repository_container import RepositoryContainer
from composition.services.service_container import ServiceContainer


def build_estates_container(
    infrastructure: InfrastructureContainer,
    repositories: RepositoryContainer,
    services: ServiceContainer,
) -> EstatesContainer:
    transactions = infrastructure.transactions

    return EstatesContainer(
        create=CreateEstateUseCase(
            transactions,
            services.estates,
            services.authorization,
            services.estate_participants,
        ),
        update=UpdateEstateUseCase(
            transactions,
            services.estates,
            services.authorization,
            services.estate_participants,
            infrastructure.object_storage,
        ),
        delete=DeleteEstateUseCase(
            transactions,
            repositories.estates,
            services.authorization,
        ),
        suggest=SuggestEstateUseCase(transactions, services.estates),
        get_one=GetEstateUseCase(
            transactions,
            repositories.estates,
            services.authorization,
        ),
        get_filtered=GetFilteredEstateUseCase(
            transactions,
            services.estates,
        ),
        toggle_saved=ToggleSavedEstateUseCase(
            transactions,
            repositories.estates,
        ),
        email_agent=EmailToAgentUseCase(
            transactions,
            repositories.estates,
            infrastructure.mailer,
            infrastructure.urls.app_base_url,
        ),
    )
