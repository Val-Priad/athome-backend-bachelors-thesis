from application.admin.change_user_role_use_case import ChangeUserRoleUseCase
from application.admin.delete_admin_user_use_case import DeleteAdminUserUseCase
from application.admin.get_admin_user_use_case import GetAdminUserUseCase
from application.auth.login_user_use_case import LoginUserUseCase
from application.auth.register_user_use_case import RegisterUserUseCase
from application.auth.resend_verification_use_case import (
    ResendVerificationUseCase,
)
from application.auth.reset_password_use_case import ResetPasswordUseCase
from application.auth.verify_email_use_case import VerifyEmailUseCase
from application.auth.verify_new_password_use_case import (
    VerifyNewPasswordUseCase,
)
from application.users.delete_me_use_case import DeleteMeUseCase
from application.users.get_me_use_case import GetMeUseCase
from application.users.update_password_use_case import UpdatePasswordUseCase
from application.users.update_personal_data_use_case import (
    UpdatePersonalDataUseCase,
)
from domain.admin.services.admin_users_service import AdminUsersService
from domain.email_verification.email_verification_repository import (
    EmailVerificationRepository,
)
from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from domain.password_reset.password_reset_repository import (
    PasswordResetRepository,
)
from domain.password_reset.password_reset_service import PasswordResetService
from domain.user.services.auth_service import AuthService
from domain.user.services.me_service import MeService
from domain.user.user_repository import UserRepository
from infrastructure.email.Mailer import Mailer
from security import PasswordCrypto, TokenCrypto

# EXTERNAL
mailer = Mailer()

# INTERNAL
password_hasher = PasswordCrypto()
token_hasher = TokenCrypto()

# DOMAIN RELATED
user_repository = UserRepository()

email_verification_repository = EmailVerificationRepository()
email_verification_service = EmailVerificationService(
    email_verification_repository, user_repository, mailer, token_hasher
)

password_reset_repository = PasswordResetRepository()
password_reset_service = PasswordResetService(
    password_reset_repository,
    user_repository,
    mailer,
    token_hasher,
    password_hasher,
)

auth_service = AuthService(user_repository, password_hasher, email_verification_service)
me_service = MeService(user_repository, password_hasher)
admin_users_service = AdminUsersService(user_repository)


register_user_use_case = RegisterUserUseCase(auth_service, email_verification_service)
verify_email_use_case = VerifyEmailUseCase(email_verification_service)
resend_verification_use_case = ResendVerificationUseCase(email_verification_service)
login_user_use_case = LoginUserUseCase(auth_service)
reset_password_use_case = ResetPasswordUseCase(password_reset_service)
verify_new_password_use_case = VerifyNewPasswordUseCase(password_reset_service)


get_me_use_case = GetMeUseCase(me_service)
delete_me_use_case = DeleteMeUseCase(me_service)
update_password_use_case = UpdatePasswordUseCase(me_service)
update_personal_data_use_case = UpdatePersonalDataUseCase(me_service)

get_admin_user_use_case = GetAdminUserUseCase(admin_users_service)
change_user_role_use_case = ChangeUserRoleUseCase(admin_users_service)
delete_admin_user_use_case = DeleteAdminUserUseCase(admin_users_service)
