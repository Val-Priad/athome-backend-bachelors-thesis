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
from composition.infrastructure.infrastructure_container import (
    InfrastructureContainer,
)
from composition.modules.auth.auth_container import AuthContainer
from composition.repositories.repository_container import RepositoryContainer
from composition.services.service_container import ServiceContainer


def build_auth_container(
    infrastructure: InfrastructureContainer,
    repositories: RepositoryContainer,
    services: ServiceContainer,
) -> AuthContainer:
    transactions = infrastructure.transactions
    mailer = infrastructure.mailer

    return AuthContainer(
        register_user=RegisterUserUseCase(
            transactions=transactions,
            auth_service=services.auth,
            email_verification_service=services.email_verification,
            mailer=mailer,
        ),
        login_user=LoginUserUseCase(
            transactions=transactions,
            auth_service=services.auth,
        ),
        verify_email=VerifyEmailUseCase(
            transactions=transactions,
            email_verification_service=services.email_verification,
        ),
        resend_verification=ResendVerificationUseCase(
            transactions=transactions,
            email_verification_service=services.email_verification,
            user_repository=repositories.users,
            mailer=mailer,
        ),
        reset_password=ResetPasswordUseCase(
            transactions=transactions,
            password_reset_service=services.password_reset,
            user_repository=repositories.users,
            mailer=mailer,
        ),
        verify_new_password=VerifyNewPasswordUseCase(
            transactions=transactions,
            password_reset_service=services.password_reset,
        ),
    )
