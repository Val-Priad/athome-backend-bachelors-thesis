from application.admin.change_user_role_use_case import ChangeUserRoleUseCase
from application.admin.delete_admin_user_use_case import DeleteAdminUserUseCase
from application.admin.get_admin_filtered_estate_use_case import (
    GetAdminFilteredEstateUseCase,
)
from application.admin.get_admin_user_use_case import GetAdminUserUseCase
from application.admin.list_agents_use_case import ListAgentsUseCase
from application.admin.list_users_use_case import ListUsersUseCase
from application.estate.mapping.estate_response_mapper import (
    EstateResponseMapper,
)
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from composition.modules.admin.admin_container import AdminContainer
from composition.repositories.repository_container import RepositoryContainer
from composition.services.service_container import ServiceContainer


def build_admin_container(
    infrastructure: InfrastructureContainer,
    repositories: RepositoryContainer,
    services: ServiceContainer,
    estate_response_mapper: EstateResponseMapper,
) -> AdminContainer:
    transactions = infrastructure.transactions
    authorization = services.authorization

    return AdminContainer(
        get_user=GetAdminUserUseCase(
            transactions=transactions,
            authorization_service=authorization,
            user_repository=repositories.users,
        ),
        change_user_role=ChangeUserRoleUseCase(
            transactions=transactions,
            admin_users_service=services.admin_users,
            authorization_service=authorization,
        ),
        delete_user=DeleteAdminUserUseCase(
            transactions=transactions,
            admin_users_service=services.admin_users,
            authorization_service=authorization,
        ),
        list_users=ListUsersUseCase(
            transactions=transactions,
            user_repository=repositories.users,
            authorization_service=authorization,
        ),
        list_agents=ListAgentsUseCase(
            transactions=transactions,
            user_repository=repositories.users,
            authorization_service=authorization,
        ),
        get_filtered_estates=GetAdminFilteredEstateUseCase(
            transactions=transactions,
            estate_service=services.estates,
            authorization_service=authorization,
            response_mapper=estate_response_mapper,
        ),
    )
