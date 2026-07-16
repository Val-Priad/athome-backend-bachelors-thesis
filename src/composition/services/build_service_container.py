from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from composition.repositories.repository_container import RepositoryContainer
from composition.services.service_container import ServiceContainer
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


def build_service_container(
    infrastructure: InfrastructureContainer,
    repositories: RepositoryContainer,
) -> ServiceContainer:
    token_lifecycle = TokenLifecycleService()

    return ServiceContainer(
        token_lifecycle=token_lifecycle,
        authorization=AuthorizationService(repositories.users),
        email_verification=EmailVerificationService(
            repositories.email_verifications,
            infrastructure.mailer,
            infrastructure.token_hasher,
            token_lifecycle,
        ),
        password_reset=PasswordResetService(
            repositories.password_resets,
            infrastructure.mailer,
            infrastructure.token_hasher,
            infrastructure.password_hasher,
            token_lifecycle,
        ),
        auth=AuthService(
            repositories.users,
            infrastructure.password_hasher,
        ),
        me=MeService(
            repositories.users,
            infrastructure.password_hasher,
        ),
        admin_users=AdminUsersService(repositories.users),
        agents=AgentService(repositories.users),
        estates=EstateService(
            repositories.estates,
            infrastructure.vicinity_client,
        ),
        estate_participants=EstateParticipantsService(repositories.users),
    )
