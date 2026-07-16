from application.transactions import TransactionManagerProtocol
from domain.password_reset.password_reset_service import PasswordResetService
from domain.user.user_repository import UserRepository


class ResetPasswordUseCase:
    def __init__(
        self,
        transactions: TransactionManagerProtocol,
        password_reset_service: PasswordResetService,
        user_repository: UserRepository,
    ) -> None:
        self._transactions = transactions
        self._password_reset_service = password_reset_service
        self._user_repository = user_repository

    def execute(self, email: str) -> None:
        with self._transactions.session() as session:
            user = self._user_repository.get_user_by_email(session, email)
            raw_token = self._password_reset_service.get_token(
                session, user.id
            )
            email_to = user.email
        self._password_reset_service.send_reset_password_email(
            email_to, raw_token
        )
