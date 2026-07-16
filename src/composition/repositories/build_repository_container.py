from composition.repositories.repository_container import RepositoryContainer
from domain.email_verification.email_verification_repository import (
    EmailVerificationRepository,
)
from domain.estate.estate_repository import EstateRepository
from domain.password_reset.password_reset_repository import (
    PasswordResetRepository,
)
from domain.user.user_repository import UserRepository


def build_repository_container() -> RepositoryContainer:
    return RepositoryContainer(
        users=UserRepository(),
        email_verifications=EmailVerificationRepository(),
        password_resets=PasswordResetRepository(),
        estates=EstateRepository(),
    )
