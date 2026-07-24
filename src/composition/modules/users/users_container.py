from dataclasses import dataclass

from application.users.cleanup_unverified_users_use_case import (
    CleanupUnverifiedUsersUseCase,
)
from application.users.delete_me_use_case import DeleteMeUseCase
from application.users.get_me_use_case import GetMeUseCase
from application.users.update_password_use_case import UpdatePasswordUseCase
from application.users.update_personal_data_use_case import (
    UpdatePersonalDataUseCase,
)


@dataclass(frozen=True, slots=True)
class UsersContainer:
    get_me: GetMeUseCase
    delete_me: DeleteMeUseCase
    update_password: UpdatePasswordUseCase
    update_personal_data: UpdatePersonalDataUseCase
    cleanup_unverified: CleanupUnverifiedUsersUseCase
