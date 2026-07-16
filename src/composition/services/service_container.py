from dataclasses import dataclass

from domain.admin.services.admin_users_service import AdminUsersService
from domain.email_verification.email_verification_service import (
    EmailVerificationService,
)
from domain.estate.estate_participants_service import EstateParticipantsService
from domain.estate.estate_service import EstateService
from domain.password_reset.password_reset_service import PasswordResetService
from domain.token.token_lifecycle_service import TokenLifecycleService
from domain.user.services.agent_service import AgentService
from domain.user.services.auth_service import AuthService
from domain.user.services.me_service import MeService
from security.authorization import AuthorizationService


@dataclass(frozen=True, slots=True)
class ServiceContainer:
    token_lifecycle: TokenLifecycleService
    authorization: AuthorizationService
    email_verification: EmailVerificationService
    password_reset: PasswordResetService
    auth: AuthService
    me: MeService
    admin_users: AdminUsersService
    agents: AgentService
    estates: EstateService
    estate_participants: EstateParticipantsService
