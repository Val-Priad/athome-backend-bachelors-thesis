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
from domain.media.media_service import MediaService
from domain.media.media_usage_service import MediaUsageService
from domain.password_reset.password_reset_service import PasswordResetService
from domain.token.token_generator import TokenGenerator
from domain.token.token_lifecycle_service import TokenLifecycleService
from domain.user.services.agent_service import AgentService
from domain.user.services.auth_service import AuthService
from domain.user.services.authorization import AuthorizationService
from domain.user.services.me_service import MeService
from domain.user.services.password_hasher import PasswordHasher


def build_service_container(
    infrastructure: InfrastructureContainer,
    repositories: RepositoryContainer,
) -> ServiceContainer:
    token_lifecycle = TokenLifecycleService()
    token_generator = TokenGenerator()
    password_hasher = PasswordHasher()
    media_service = MediaService(infrastructure.object_storage)

    return ServiceContainer(
        token_lifecycle=token_lifecycle,
        authorization=AuthorizationService(
            user_repository=repositories.users,
        ),
        email_verification=EmailVerificationService(
            email_verification_repository=repositories.email_verifications,
            token_generator=token_generator,
            token_lifecycle_service=token_lifecycle,
        ),
        password_reset=PasswordResetService(
            password_reset_repository=repositories.password_resets,
            token_generator=token_generator,
            password_hasher=password_hasher,
            token_lifecycle_service=token_lifecycle,
        ),
        auth=AuthService(
            user_repository=repositories.users,
            password_hasher=password_hasher,
        ),
        me=MeService(
            user_repository=repositories.users,
            password_hasher=password_hasher,
        ),
        admin_users=AdminUsersService(
            user_repository=repositories.users,
        ),
        agents=AgentService(
            user_repository=repositories.users,
        ),
        media=media_service,
        media_usage=MediaUsageService(
            estate_media_repository=repositories.estate_media,
            user_repository=repositories.users,
        ),
        estates=EstateService(
            estate_repository=repositories.estates,
            vicinity_client=infrastructure.vicinity_client,
        ),
        estate_participants=EstateParticipantsService(
            user_repository=repositories.users,
        ),
    )
