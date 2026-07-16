from application.users.delete_me_use_case import DeleteMeUseCase
from application.users.get_me_use_case import GetMeUseCase
from application.users.update_password_use_case import UpdatePasswordUseCase
from application.users.update_personal_data_use_case import (
    UpdatePersonalDataUseCase,
)
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from composition.modules.users.users_container import UsersContainer
from composition.repositories.repository_container import RepositoryContainer
from composition.services.service_container import ServiceContainer


def build_users_container(
    infrastructure: InfrastructureContainer,
    repositories: RepositoryContainer,
    services: ServiceContainer,
) -> UsersContainer:
    transactions = infrastructure.transactions

    return UsersContainer(
        get_me=GetMeUseCase(
            transactions=transactions,
            user_repository=repositories.users,
        ),
        delete_me=DeleteMeUseCase(
            transactions=transactions,
            user_repository=repositories.users,
        ),
        update_password=UpdatePasswordUseCase(
            transactions=transactions,
            me_service=services.me,
        ),
        update_personal_data=UpdatePersonalDataUseCase(
            transactions=transactions,
            me_service=services.me,
        ),
    )
