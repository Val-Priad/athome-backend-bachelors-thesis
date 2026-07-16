from application.admin.change_user_role_use_case import ChangeUserRoleUseCase
from application.admin.delete_admin_user_use_case import DeleteAdminUserUseCase
from application.admin.get_admin_filtered_estate_use_case import (
    GetAdminFilteredEstateUseCase,
)
from application.admin.get_admin_user_use_case import GetAdminUserUseCase
from application.admin.list_agents_use_case import ListAgentsUseCase
from application.admin.list_users_use_case import ListUsersUseCase
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
) -> AdminContainer:
    transactions = infrastructure.transactions
    authorization = services.authorization

    return AdminContainer(
        get_user=GetAdminUserUseCase(
            transactions,
            services.admin_users,
            authorization,
            repositories.users,
        ),
        change_user_role=ChangeUserRoleUseCase(
            transactions,
            services.admin_users,
            authorization,
        ),
        delete_user=DeleteAdminUserUseCase(
            transactions,
            services.admin_users,
            authorization,
        ),
        list_users=ListUsersUseCase(
            transactions,
            repositories.users,
            authorization,
        ),
        list_agents=ListAgentsUseCase(
            transactions,
            repositories.users,
            authorization,
        ),
        get_filtered_estates=GetAdminFilteredEstateUseCase(
            transactions,
            services.estates,
            authorization,
        ),
    )
