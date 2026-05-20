from domain.password_reset.password_reset_service import PasswordResetService
from domain.user.user_repository import UserRepository
from infrastructure.db import db_session


class ResetPasswordUseCase:
    def __init__(
        self,
        password_reset_service: PasswordResetService,
        user_repository: UserRepository,
    ):
        self.password_reset_service = password_reset_service
        self.user_repository = user_repository

    def execute(self, email: str) -> None:
        with db_session() as session:
            user = self.user_repository.get_user_by_email(session, email)
            raw_token = self.password_reset_service.get_token(session, user.id)
            email_to = user.email
        self.password_reset_service.send_reset_password_email(
            email_to, raw_token
        )
