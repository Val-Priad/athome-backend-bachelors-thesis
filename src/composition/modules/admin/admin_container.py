from dataclasses import dataclass

from application.admin.change_user_role_use_case import ChangeUserRoleUseCase
from application.admin.delete_admin_user_use_case import DeleteAdminUserUseCase
from application.admin.get_admin_filtered_estate_use_case import (
    GetAdminFilteredEstateUseCase,
)
from application.admin.get_admin_user_use_case import GetAdminUserUseCase
from application.admin.list_agents_use_case import ListAgentsUseCase
from application.admin.list_users_use_case import ListUsersUseCase


@dataclass(frozen=True, slots=True)
class AdminContainer:
    get_user: GetAdminUserUseCase
    change_user_role: ChangeUserRoleUseCase
    delete_user: DeleteAdminUserUseCase
    list_users: ListUsersUseCase
    list_agents: ListAgentsUseCase
    get_filtered_estates: GetAdminFilteredEstateUseCase
