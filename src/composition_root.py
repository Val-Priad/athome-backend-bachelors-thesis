# ============================================================================
# IMPORTS
# ============================================================================

# Infrastructure Layer
from application.admin.change_user_role_use_case import ChangeUserRoleUseCase
from application.admin.delete_admin_user_use_case import DeleteAdminUserUseCase

# Application Layer - Admin Use Cases
from application.admin.get_admin_filtered_estate_use_case import (
    GetAdminFilteredEstateUseCase,
)
from application.admin.get_admin_user_use_case import GetAdminUserUseCase
from application.admin.list_agents_use_case import ListAgentsUseCase
from application.admin.list_users_use_case import ListUsersUseCase

# Application Layer - Agent Use Cases
from application.agent.get_agent_description_use_case import (
    GetAgentDescriptionUseCase,
)
from application.auth.login_user_use_case import LoginUserUseCase

# Application Layer - Auth Use Cases
from application.auth.register_user_use_case import RegisterUserUseCase
from application.auth.resend_verification_use_case import (
    ResendVerificationUseCase,
)
from application.auth.reset_password_use_case import ResetPasswordUseCase
from application.auth.verify_email_use_case import VerifyEmailUseCase
from application.auth.verify_new_password_use_case import (
    VerifyNewPasswordUseCase,
)
from application.estate.create_estate_use_case import CreateEstateUseCase
from application.estate.get_estate_use_case import GetEstateUseCase
from application.estate.get_filtered_estate_use_case import (
    GetFilteredEstateUseCase,
)
from application.estate.suggest_estate_use_case import SuggestEstateUseCase

# Application Layer - Estate Use Cases
from application.estate.toggle_saved_estate_use_case import (
    ToggleSavedEstateUseCase,
)
from application.users.delete_me_use_case import DeleteMeUseCase

# Application Layer - Users Use Cases
from application.users.get_me_use_case import GetMeUseCase
from application.users.update_password_use_case import UpdatePasswordUseCase
from application.users.update_personal_data_use_case import (
    UpdatePersonalDataUseCase,
)
from domain.admin.services.admin_users_service import AdminUsersService
from domain.email_verification.email_verification_repository import (
    EmailVerificationRepository,
)

# Domain Layer - Services
from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)

# Domain Layer - Repositories
from domain.estate.estate_participants_service import EstateParticipantsService
from domain.estate.estate_repository import EstateRepository
from domain.estate.estate_service import EstateService
from domain.password_reset.password_reset_repository import (
    PasswordResetRepository,
)
from domain.password_reset.password_reset_service import PasswordResetService
from domain.token.token_lifecycle_service import TokenLifecycleService
from domain.user.services.agent_service import AgentService
from domain.user.services.auth_service import AuthService
from domain.user.services.me_service import MeService
from domain.user.user_repository import UserRepository
from infrastructure.email.Mailer import Mailer
from infrastructure.vicinity.retry_vicinity_client import (
    RetryingVicinityClient,
)
from infrastructure.vicinity.vicinity_client import (
    OpenStreetMapVicinityClient,
)
from security import AuthorizationService, PasswordCrypto, TokenCrypto

# ============================================================================
# INFRASTRUCTURE LAYER INITIALIZATION
# ============================================================================

mailer = Mailer()
password_hasher = PasswordCrypto()
token_hasher = TokenCrypto()


# ============================================================================
# DOMAIN LAYER INITIALIZATION
# ============================================================================

# Repositories
user_repository = UserRepository()
email_verification_repository = EmailVerificationRepository()
password_reset_repository = PasswordResetRepository()
estate_repository = EstateRepository()
osm_vicinity_client = OpenStreetMapVicinityClient()
vicinity_client = RetryingVicinityClient(osm_vicinity_client)

# Services
token_lifecycle_service = TokenLifecycleService()
authorization_service = AuthorizationService(user_repository)
email_verification_service = EmailVerificationService(
    email_verification_repository,
    mailer,
    token_hasher,
    token_lifecycle_service,
)

password_reset_service = PasswordResetService(
    password_reset_repository,
    mailer,
    token_hasher,
    password_hasher,
    token_lifecycle_service,
)

auth_service = AuthService(user_repository, password_hasher)
me_service = MeService(user_repository, password_hasher)
admin_users_service = AdminUsersService(user_repository)
agent_service = AgentService(user_repository)
estate_service = EstateService(estate_repository, vicinity_client)
estate_participants_service = EstateParticipantsService(user_repository)


# ============================================================================
# APPLICATION LAYER INITIALIZATION
# ============================================================================

# Auth Use Cases
register_user_use_case = RegisterUserUseCase(
    auth_service, email_verification_service
)
login_user_use_case = LoginUserUseCase(auth_service)
verify_email_use_case = VerifyEmailUseCase(email_verification_service)
resend_verification_use_case = ResendVerificationUseCase(
    email_verification_service, user_repository
)
reset_password_use_case = ResetPasswordUseCase(
    password_reset_service, user_repository
)
verify_new_password_use_case = VerifyNewPasswordUseCase(password_reset_service)

# Users Use Cases
get_me_use_case = GetMeUseCase(user_repository)
delete_me_use_case = DeleteMeUseCase(user_repository)
update_password_use_case = UpdatePasswordUseCase(me_service)
update_personal_data_use_case = UpdatePersonalDataUseCase(me_service)

# Admin  Use Cases
get_admin_user_use_case = GetAdminUserUseCase(
    admin_users_service, authorization_service, user_repository
)
change_user_role_use_case = ChangeUserRoleUseCase(
    admin_users_service, authorization_service
)
delete_admin_user_use_case = DeleteAdminUserUseCase(
    admin_users_service, authorization_service
)
list_users_use_case = ListUsersUseCase(user_repository, authorization_service)
get_admin_filtered_estate_use_case = GetAdminFilteredEstateUseCase(
    estate_service, authorization_service
)
list_agents_use_case = ListAgentsUseCase(
    user_repository, authorization_service
)

# Agent Use Cases
get_agent_description_use_case = GetAgentDescriptionUseCase(agent_service)

# Estate Use Cases
create_estate_use_case = CreateEstateUseCase(
    estate_service, authorization_service, estate_participants_service
)
suggest_estate_use_case = SuggestEstateUseCase(estate_service)
get_estate_use_case = GetEstateUseCase(
    estate_repository, authorization_service
)
get_filtered_estate_use_case = GetFilteredEstateUseCase(estate_service)
toggle_saved_estate_use_case = ToggleSavedEstateUseCase(estate_repository)
